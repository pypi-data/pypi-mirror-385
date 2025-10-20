"""Core handlers for Rich output formatting in Loguru logging calls."""

from typing import Callable
from typing_extensions import Unpack

from datetime import datetime

import logging
from logging import LogRecord
from loguru import logger

from rich.console import ConsoleRenderable
from rich.logging import RichHandler
from rich.table import Table
from rich.text import Text
from rich.traceback import Traceback

from nebulog.core import LOG_LEVEL_JUSTIFICATION, TimeDisplayMode, TracebackMode
from nebulog.interfaces import MessageFormatter, TimeRenderer
from nebulog.renderers import (
    HiddenTimeRenderer,
    InlineTimeRenderer,
    SeparateLineTimeRenderer,
    style_renderer,
)
from nebulog.types import RichHandlerKwargs


class LoguruHandler(logging.Handler):
    """Bridge Loguru with the Standard Library logging module."""

    def emit(self, record: LogRecord) -> None:
        """Emit a log record to Loguru.

        This method bridges the standard library logging module with Loguru, converting
        log records from the standard library to Loguru's logging system. It handles the
        conversion of PSL log levels to Loguru levels and properly managers exception
        information, stack frame depth etc. for accurate logging context.

        Parameters
        ----------
        record : LogRecord
            The information pertinent to the event being logged.
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class NebulogHandler(RichHandler):
    """A logging handler that extends RichHandler for structured console output.

    This handler integrates Rich library capabilities with Loguru-style logging,
    providing flexible time display modes, custom message rendering, and enhanced
    traceback handling for console output.

    Parameters
    ----------
    time_display_mode : TimeDisplayMode
        Controls the position of the log timestamp. Valid values are:

        - TimeDisplayMode.SEPARATE_LINE
        - TimeDisplayMode.INLINE_LEFT
        - TimeDisplayMode.INLINE_RIGHT
        - TimeDisplayMode.HIDDEN
    log_time_format : str
        String for `strftime` that formats the time.
    traceback_mode : TracebackMode, default TracebackMode.SUPPRESS
        Controls whether tracebacks are displayed in the console or not when an
        exception is caught. Valid values are:

        - TracebackMode.SUPPRESS
        - TracebackMode.RICH
    time_renderer : TimeRenderer, optional
        A class that inherits from the `TimeRenderer` ABC class to control how the
        log timestamp is handled by Rich.
    message_renderer : BaseMessageFormatter, optional
        A class that inherits from the `BaseMessageFormatter` ABC class to control how
        the log message is handled by Rich. Log level and filename should not be defined
        as `NebulogHandler` directly handles their output.
    **kwargs
        Extra arguments to instatiate a `RichHandler` object for fine-tuning logging
        controls.
    """

    def __init__(
        self,
        time_display_mode: TimeDisplayMode,
        log_time_format: str,
        traceback_mode: TracebackMode = TracebackMode.SUPPRESS,
        time_renderer: TimeRenderer | None = None,
        message_renderer: MessageFormatter | type[MessageFormatter] | None = None,
        **kwargs: Unpack[RichHandlerKwargs],
    ) -> None:
        super().__init__(log_time_format=log_time_format, **kwargs)

        self.time_display_mode = time_display_mode

        self.time_renderer = self._create_timestamp_renderer(time_renderer)
        self.message_renderer = self._create_message_renderer(message_renderer)

        self.traceback_mode = traceback_mode

        self._setup_display_configuration()

    def emit(self, record: LogRecord) -> None:
        """Override method to handle how tracebacks will be rendered.

        Parameters
        ----------
        record : LogRecord
            The information pertinent to the event being logged.
        """
        if record.exc_info and self.traceback_mode == TracebackMode.RICH:
            # Create message-only record
            original_exc_info = record.exc_info

            record.exc_info = None
            record.exc_text = None

            super().emit(record)

            # Render full-width traceback separately
            traceback = Traceback.from_exception(
                exc_type=original_exc_info[0],  # type: ignore[arg-type]
                exc_value=original_exc_info[1],  # type: ignore[arg-type]
                traceback=original_exc_info[2],
                width=self.tracebacks_width,
                code_width=self.tracebacks_code_width,
                extra_lines=self.tracebacks_extra_lines,
                theme=self.tracebacks_theme,
                word_wrap=self.tracebacks_word_wrap,
                show_locals=self.tracebacks_show_locals,
                locals_max_length=self.locals_max_length,
                locals_max_string=self.locals_max_string,
                suppress=self.tracebacks_suppress,
                max_frames=self.tracebacks_max_frames,
            )
            self.console.print(traceback)

        elif self.traceback_mode == TracebackMode.SUPPRESS:
            record.exc_info = None
            record.exc_text = None

            super().emit(record)

        else:
            super().emit(record)

    def _create_message_renderer(
        self, message_renderer: MessageFormatter | type[MessageFormatter] | None
    ) -> Callable[[str], ConsoleRenderable]:
        """Define the mechanism through which messages will be rendered."""
        if message_renderer is None:
            return Text

        # Instatiate renderer
        renderer = message_renderer()  # type: ignore[operator]

        return renderer.format_message

    def _get_log_time(self, record: LogRecord) -> str:
        """Get the record time based on `log_time_format` to handle line repeats."""
        safe_time_fmt = str(self._log_render.time_format)

        return datetime.fromtimestamp(record.created).strftime(safe_time_fmt)

    def render_message(self, record: LogRecord, message: str) -> ConsoleRenderable:
        """Render message text based on `TimeDisplayMode` and `MessageFormatter`.

        Parameters
        ----------
        record : LogRecord
            The logging record.
        message : str
            String containing log message.

        Returns
        -------
        ConsoleRenderable
            Renderable to display log message.
        """
        log_time_string = self._get_log_time(record)

        should_show_time = self._should_show_time(log_time_string)

        # Dispatch to appropriate rendering method based on display mode
        if self.time_display_mode == TimeDisplayMode.SEPARATE_LINE:
            return self._render_separate_line_message(
                record, message, log_time_string, should_show_time=should_show_time
            )

        if self.time_display_mode in (
            TimeDisplayMode.INLINE_LEFT,
            TimeDisplayMode.INLINE_RIGHT,
        ):
            return self._render_inline_message(
                record, message, log_time_string, should_show_time=should_show_time
            )

        if self.time_display_mode == TimeDisplayMode.HIDDEN:
            return self._render_hidden_time_message(record, message)

        # Fallback to standard processing
        return self._process_message_markup(record, message)

    def _render_separate_line_message(
        self,
        record: LogRecord,
        message: str,
        log_time_string: str,
        *,
        should_show_time: bool,
    ) -> ConsoleRenderable:
        """Handle separate line time display."""
        if should_show_time:
            time_renderable = self.time_renderer.render_time(log_time_string)

            if time_renderable:
                self.console.print(time_renderable)

            self._update_last_time(log_time_string)

        return self._process_message_markup(record, message)

    def _render_hidden_time_message(
        self, record: LogRecord, message: str
    ) -> ConsoleRenderable:
        """Handle hidden time display."""
        return self._process_message_markup(record, message)

    def _should_show_time(self, log_time_string: str) -> bool:
        """Check if time should be displayed based on `omit_repeated_times`."""
        if (
            not hasattr(self._log_render, "omit_repeated_times")
            or not self._log_render.omit_repeated_times
        ):
            return True

        last_time = getattr(self._log_render, "_last_time", None)
        return last_time is None or log_time_string != last_time

    def _update_last_time(self, log_time_string: str) -> None:
        """Update the last recorded log time."""
        self._log_render._last_time = log_time_string  # type: ignore[assignment]

    def _create_timestamp_renderer(
        self, time_renderer: TimeRenderer | None
    ) -> TimeRenderer:
        """Create default time renderer based on `TimeDisplayMode`."""
        # Check if it a class to be instatiated
        if time_renderer is not None and isinstance(time_renderer, type):
            return time_renderer()

        if time_renderer is not None:
            return time_renderer

        if self.time_display_mode == TimeDisplayMode.SEPARATE_LINE:
            return SeparateLineTimeRenderer()

        if self.time_display_mode in (
            TimeDisplayMode.INLINE_LEFT,
            TimeDisplayMode.INLINE_RIGHT,
        ):
            return InlineTimeRenderer()

        return HiddenTimeRenderer()

    def _setup_display_configuration(self) -> None:
        """Configure log structure settings based on `TimeDisplayMode`."""
        inline_modes = (TimeDisplayMode.INLINE_LEFT, TimeDisplayMode.INLINE_RIGHT)

        self.show_time = self.time_display_mode in inline_modes

        self._log_render.show_level = (
            self.time_display_mode != TimeDisplayMode.INLINE_LEFT
        )

    def _process_message_markup(
        self, record: LogRecord, message: str
    ) -> ConsoleRenderable:
        """Process a message with extra attributes for Rich (style, markup etc.)."""
        extra = getattr(record, "extra", {})

        # Determine the Rich styling for the whole message or highlighter specifics
        if "style" in extra:
            record.highlighter = style_renderer(extra["style"])

        elif "highlighter" in extra:
            resolved_highlighter = self._handle_custom_highlighter(extra["highlighter"])
            record.highlighter = resolved_highlighter

        # Processes the Rich content provided to the logging call
        if "rich" in extra:
            chosen_message = extra["rich"]

        elif "alt" in extra:
            chosen_message = extra["alt"]

        else:
            rendered = super().render_message(record, message)

            if isinstance(rendered, Text):
                chosen_message = rendered.markup

            else:
                chosen_message = str(rendered)

        return self.message_renderer(chosen_message)

    def _handle_custom_highlighter(self, highlighter_arg):
        """Resolve Rich highlighter if "highlighter" is specified for the log call."""
        # Check if it a class to be instatiated
        if isinstance(highlighter_arg, type):
            return highlighter_arg()

        # Check if it is an already instatiated class with the highlight method
        if hasattr(highlighter_arg, "highlight") and callable(
            highlighter_arg.highlight
        ):
            return highlighter_arg

        return None

    def _create_inline_grid(
        self,
        time_text: ConsoleRenderable | None,
        level_text: Text,
        message_renderable: ConsoleRenderable,
    ) -> Table:
        """Create a grid layout for inline time display."""
        grid = Table.grid(expand=True, padding=(0, 1))

        if self.time_display_mode == TimeDisplayMode.INLINE_LEFT:
            grid.add_column(justify="left", no_wrap=True)  # Time
            grid.add_column(justify="left", no_wrap=True)  # Level
            grid.add_column(justify="left", ratio=1)  # Message

            grid.add_row(time_text, level_text, message_renderable)

        elif self.time_display_mode == TimeDisplayMode.INLINE_RIGHT:
            grid.add_column(justify="left", ratio=1)  # Message
            grid.add_column(justify="right", no_wrap=True)  # Time

            grid.add_row(message_renderable, time_text)

        return grid

    def _render_inline_message(
        self,
        record: LogRecord,
        message: str,
        log_time_string: str,
        *,
        should_show_time: bool,
    ) -> ConsoleRenderable:
        """Render message with inline time using `Table.grid` for layout."""
        plain_time = Text.from_markup(log_time_string).plain

        time_renderable = self.time_renderer.render_time(log_time_string)
        message_renderable = self._process_message_markup(record, message)

        # Create level text
        level = record.levelname
        level_lower = level.lower()

        level_text = Text(
            level.ljust(LOG_LEVEL_JUSTIFICATION), style=f"logging.level.{level_lower}"
        )

        # Handle time visibility
        if not should_show_time:
            time_renderable = Text(" " * len(plain_time))

        grid = self._create_inline_grid(time_renderable, level_text, message_renderable)
        self._update_last_time(log_time_string)

        return grid
