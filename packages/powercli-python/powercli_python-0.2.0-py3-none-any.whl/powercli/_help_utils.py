"""
Utilities for working with help messages.
"""

from __future__ import annotations

__all__ = [
    "len",
    "terminal_width",
    "help_message",
    "usage",
    "options",
    "examples",
    "pretty_flag",
    "values",
    "commands",
    "positional_blocks",
]

import builtins
import shlex
import shutil
from collections.abc import Collection
from functools import partial
from hashlib import blake2s
from itertools import chain
from typing import TYPE_CHECKING, Any

import wraptext
from adorable import color
from adorable.color import Color
from adorable.common import BLACK, BOLD, MAROON, NAVY

from .static import Static

if TYPE_CHECKING:
    from .args import Flag
    from .category import Category
    from .command import Command


PROMPT_PREFIX = "$"


def _color_for_category(category: Category | None) -> Color[Any]:
    if category is None:
        return color.Colorless.from_rgb(0)
    elif isinstance(category.color, Color):
        return category.color
    else:
        return color.from_rgb(
            category.color or blake2s(category.title.encode()).digest()[0]
        )


# See also: https://phoenixr-codes.github.io/adorable/caution-ansi-strings.html#getting-the-visible-length-of-a-string
def len(x: Any, /) -> int:
    """Returns the length of an object.

    In case of a string, it ignores ANSI escape sequences.
    """
    if isinstance(x, str):
        return wraptext._display_len(x)  # type: ignore
    return builtins.len(x)


def terminal_width() -> int:
    """Returns the amount of columns of the terminal."""
    return shutil.get_terminal_size().columns


def _indent_text(text: str, indent: str, *, indent_initial: bool) -> str:
    """Indents each line with `indent` after wrapping it to a maximum with of the terminal's width.

    If `indent_initial` is `False`, then the first line is not indented.
    """
    wrap = partial(
        wraptext.wrap,
        width=terminal_width(),
        expand_tabs=False,
        replace_whitespace=False,
        fix_sentence_endings=False,
        drop_whitespace=False,
    )
    blocks = text.splitlines()
    lines = []
    for i, block in enumerate(blocks):
        if i == 0 and not indent_initial:
            lines.extend(wrap(block, subsequent_indent=indent))
        else:
            lines.extend(wrap(block, initial_indent=indent, subsequent_indent=indent))
    return "\n".join(lines)


def _add_description(
    lhs: str,
    *,
    indent: int,
    description: str | None,
    long_description: str | None,
    description_indentation: int = 31,
    tags: Collection[str] | None = None,
) -> str:
    """
    Adds the short and long description of something by indenting it
    appropriately.

    # Parameters

    * `lhs` - The text on the left hand side (e.g. flag name with prefix).
    * `indent` - The amount of indentation to indent text on the right side
      where it spans over the first line.
    * `description` - The (short) description.
    * `long_description` - The long description.
    * `description_indentation` - The amount of columns next to the
      argument/command name(s) required to put the description there. Otherwise
      the first line is placed underneath.
    * `tags` - Additional tags to append to the right hand side.
    """
    text = " " * indent + lhs
    full_description = ""
    if description is not None:
        full_description += description
    if long_description is not None:
        if full_description:
            full_description += f"\n\n{long_description}"
        else:
            full_description = long_description
    if tags is not None and len(tags) > 0:
        if full_description:
            full_description += " "
        full_description += " ".join(tags)
    if full_description:
        space_between = description_indentation - len(text)
        if space_between <= 0:
            text += "\n"
            text += _indent_text(
                full_description,
                indent=" " * description_indentation,
                indent_initial=True,
            )
        else:
            text = _indent_text(
                text + " " * space_between + full_description,
                indent=" " * description_indentation,
                indent_initial=False,
            )
    return text


def help_message(cmd: Command[Any, Any]) -> str:
    """Creates a help message for a command."""
    lines = []
    if cmd.description is not None:
        lines.append(cmd.description)
    if cmd.long_description is not None:
        if lines:
            lines.append("")
        lines.append(cmd.long_description)
    if lines:
        lines.append("")
    lines.append(usage(cmd))
    lines.append("")
    if cmd.has_flag():
        lines.append(options(cmd))
        lines.append("")
    if cmd.has_subcommand():
        lines.append(commands(cmd))
        lines.append("")
    if cmd.examples:
        lines.append(examples(cmd))
        lines.append("")
    if cmd.epilog is not None:
        lines.append("")
        lines.append(cmd.epilog)
    return "\n".join(lines)


def usage(cmd: Command[Any, Any]) -> str:
    """Returns a "usage" line for a command."""
    return (
        f"{BOLD:Usage:} {' '.join([*map(lambda p: p.name, cmd.parents()), cmd.name])}"
        f"{' [OPTIONS]' if cmd.has_flag() else ''}"
        f"{' [COMMAND]' if cmd.has_subcommand() else ''}"
        f"{' ' + positional_blocks(cmd) if positional_blocks(cmd) else ''}"
    )


def options(cmd: Command[Any, Any]) -> str:
    """Returns the usage for a command."""
    lines = []
    lines.append(f"{BOLD:Options:}")
    categories: dict[Category | None, list[Flag[Any, Any, Any]]] = {}
    for flag in cmd._flags:
        flgs = categories.setdefault(flag.category, [])
        flgs.append(flag)
    for flag in chain.from_iterable(categories.values()):
        lines.extend(pretty_flag(cmd, flag).splitlines())
    return "\n".join(lines)


def examples(cmd: Command[Any, Any]) -> str:
    """Returns examples of a command."""
    lines = []
    lines.append(f"{BOLD:Examples:}")
    lines.append("")
    for example in cmd.examples:
        if example.description:
            lines.append(
                f"{BOLD:{_indent_text(example.description, indent='  ', indent_initial=True)}}"
            )
        command_line = f"{PROMPT_PREFIX} {cmd._subcommand_path()} {' '.join(shlex.quote(arg) for arg in example.args)}"
        # TODO: syntax highlighting
        lines.append(_indent_text(command_line, indent="  ", indent_initial=True))
        lines.append("")
    return "\n".join(lines)


def pretty_flag(cmd: Command[Any, Any], flag: Flag[Any, Any, Any]) -> str:
    """Returns a descriptive information for a flag."""
    parts = []
    category = flag.category
    clr = _color_for_category(category)
    if flag.short is not None and cmd.prefix_short is not None:
        parts.extend(
            [f"{clr:{cmd.prefix_short + name}}" for name in flag.visible_short_names()]
        )
    if flag.long is not None and cmd.prefix_long is not None:
        parts.extend(
            [f"{clr:{cmd.prefix_long + name}}" for name in flag.visible_long_names()]
        )
    tags = []
    tag_text_color = BLACK
    if isinstance(flag.deprecation, Static) and flag.deprecation.value:
        tags.append(f"{tag_text_color.on(MAROON):(deprecated)}")
    if isinstance(flag.required, Static) and (
        isinstance(flag.required.value, str) or flag.required.value
    ):
        tags.append(f"{tag_text_color.on(NAVY):(required)}")
    if isinstance(flag.default, Static):
        tags.append(f"{BOLD:(default: {' '.join(map(str, flag.default.value))})}")
    return _add_description(
        f"{', '.join(parts)} {values(flag)}",
        indent=2,
        description=flag.description,
        long_description=flag.long_description,
        tags=tags,
    )


def values(flag: Flag[Any, Any, Any]) -> str:
    """Returns the values of a flag."""
    result = ""
    for value in flag.values:
        if value is Ellipsis:
            result += "..."
        else:
            result += f"{' ' if result else ''}<{value[0]}>"
    return result


def commands(cmd: Command[Any, Any]) -> str:
    """Returns a descriptive information for a subcommand."""
    lines = []
    lines.append(f"{BOLD:Commands:}")
    categories: dict[Category | None, list[Command[Any, Any]]] = {}
    for command in cmd._subcommands.values():
        cmds = categories.setdefault(command.category, [])
        cmds.append(command)
    for category, commands in categories.items():
        clr = _color_for_category(category)
        for command in commands:
            lines.extend(
                _add_description(
                    f"{clr:{command.name}}",
                    indent=2,
                    description=command.description,
                    long_description=None,
                ).splitlines()
            )
    return "\n".join(lines)


def positional_blocks(cmd: Command[Any, Any]) -> str:
    """Returns a descriptive information of all positionals of a command."""
    return " ".join(
        f"<{p.name}>" if p.required else f"[{p.name}]" for p in cmd._positionals
    )
