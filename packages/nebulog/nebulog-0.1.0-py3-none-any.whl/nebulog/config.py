"""Formal API to enable Nebulog usage at runtime."""

from loguru import logger

from rich.console import Console
from rich.theme import Theme

from nebulog.core import DEFAULT_TIME_FORMAT, TimeDisplayMode, TracebackMode
from nebulog.handler import NebulogHandler
from nebulog.interfaces import MessageFormatter, TimeRenderer
from nebulog.renderers import SimpleGridFormatter


def install(  # noqa: PLR0913
    rich_console: Console | None = None,
    level: int | str = 20,
    time_format: str = DEFAULT_TIME_FORMAT,
    time_display_mode: TimeDisplayMode | str = TimeDisplayMode.SEPARATE_LINE,
    time_renderer: TimeRenderer | None = None,
    message_renderer: MessageFormatter | type[MessageFormatter] = SimpleGridFormatter,
    traceback_mode: TracebackMode | str = TracebackMode.SUPPRESS,
    keywords: list[str] | None = None,
) -> None:
    """Install Rich logging with flexible time display and traceback options.

    Parameters
    ----------
    rich_console : Console, optional
        Rich console to be used for rendering logs.
    level : int, str, default 20
        The minimum severity level from which logged messages should be sent to the
        sink.
    time_format : str, default "⟪ %Y.%m.%d %H:%M:%S ⟫"
        String for `strftime` that formats the time. Defaults to a specific timestamp
        with Rich markup predefined.
    time_display_mode : TimeDisplayMode, str, default TimeDisplayMode.SEPARATE_LINE
        Controls the position of the log timestamp. Valid values are:

        - TimeDisplayMode.SEPARATE_LINE or "separate"
        - TimeDisplayMode.INLINE_LEFT or "left"
        - TimeDisplayMode.INLINE_RIGHT or "right"
        - TimeDisplayMode.HIDDEN or "hidden"
    time_renderer : TimeRenderer, optional
        A class that inherits from the `TimeRenderer` ABC class to control how the
        log timestamp is handled by Rich.
    message_renderer : MessageFormatter, default SimpleGridFormatter
        A class that inherits from the `BaseMessageFormatter` ABC class to control how
        the log message is handled by Rich.
    traceback_mode : TracebackMode, str, default SUPPRESS
        Controls whether tracebacks are displayed in the console or not when an
        exception is caught. Valid values are:

        - TracebackMode.SUPPRESS or "suppress"
        - TracebackMode.RICH or "rich"
    """
    # Handle string conversion for enums
    time_display_mode = TimeDisplayMode(time_display_mode)
    traceback_mode = TracebackMode(traceback_mode)

    console = rich_console or Console(
        theme=Theme(
            {
                "logging.level.trace": "bright_black",
                "logging.level.debug": "bright_cyan",
                "logging.level.success": "green",
            }
        )
    )

    handler = NebulogHandler(
        console=console,
        time_display_mode=time_display_mode,
        time_renderer=time_renderer,
        message_renderer=message_renderer,
        log_time_format=time_format,
        traceback_mode=traceback_mode,
        show_time=False,  # We handle time ourselves
        show_level=False,  # We handle level rendering ourselves
        markup=True,  # If you are using NebulogHandler, you're outputting to terminal
        rich_tracebacks=True,  # Defines Rich markup, not the option for showing or not
        keywords=keywords,
    )

    logger.configure(
        handlers=[{"sink": handler, "format": (lambda _: "{message}"), "level": level}]
    )
