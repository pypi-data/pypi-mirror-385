# nebulog/types.py
"""Type definitions for the nebulog package."""

from types import ModuleType
from typing import TypedDict

from collections.abc import Sequence

from rich.console import Console
from rich.highlighter import Highlighter


class RichHandlerKwargs(TypedDict, total=False):
    """Typed dictionary covering keywords arguments to create a `RichHandler` instance.

    This includes attributes and methods that define how logging output will be
    formatted and displayed in the console.
    """

    console: Console | None
    show_time: bool
    omit_repeated_times: bool
    show_level: bool
    show_path: bool
    enable_link_path: bool
    highlighter: Highlighter | None
    markup: bool
    rich_tracebacks: bool
    tracebacks_width: int | None
    tracebacks_extra_lines: int
    tracebacks_theme: str | None
    tracebacks_word_wrap: bool
    tracebacks_show_locals: bool
    tracebacks_suppress: Sequence[str | ModuleType]
    locals_max_length: int
    locals_max_string: int
    keywords: list[str] | None
