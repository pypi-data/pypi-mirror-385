"""Custom Rich predefined renderers for usage with Nebulog sample code."""

from logging import LogRecord

from rich import box
from rich.panel import Panel
from rich.status import Status
from rich.table import Table
from rich.text import Text

from nebulog.interfaces import BaseMessageFormatter, TimeRenderer

SAMPLE_MESSAGE = (
    "This is just a sample message, but it could be much longer, and even contain new "
    "lines. It exists [b]just[/] to showcase how Nebulog can handle log messages.\n\n"
    "Why don't you try creating your own renderers? :grin:"
)


class SampleMessageFormatter(BaseMessageFormatter):
    """Example message formatter to showcase Nebulog capabilities."""

    def format_message(
        self,
        message: str,
        record: LogRecord | None = None,  # noqa: ARG002
        **kwargs: str,  # noqa: ARG002
    ) -> Table:
        """Format the message inside a grid to maintain message alignment.

        Parameters
        ----------
        message : str
            The log message to be rendered.
        record : LogRecord, optional
            The log record containing additional context (unused in this
            implementation).
        **kwargs
            Additional keyword arguments (unused in this implementation).

        Returns
        -------
        Table
            A Rich table with the grid structure.
        """
        grid = Table.grid(expand=True)

        grid.add_column(justify="left", ratio=35)
        grid.add_column(justify="left", ratio=65)

        grid_message = Panel(
            Text.from_markup(message, overflow="fold"),
            title="First column",
            subtitle="The log message",
            border_style="green",
        )
        extra_message = Panel(
            Text.from_markup(SAMPLE_MESSAGE),
            title="Second column",
            border_style="bold red",
        )

        grid.add_row(grid_message, extra_message)

        return grid


class SampleTimeRenderer(TimeRenderer):
    """Example timestamp formatter to showcase Nebulog capabilities."""

    def render_time(self, log_time: str) -> Panel:
        """Render the formatted timestamp with a `Panel` renderable.

        Parameters
        ----------
        log_time : str
            String for `strftime` that formats the time.
        """
        return Panel(Status(log_time, spinner="aesthetic"), box=box.HEAVY)
