"""Nebulog renderers for log messages."""

from typing import Callable, Literal

from rich.table import Table
from rich.text import Text

from nebulog.interfaces import BaseMessageFormatter


class SimpleGridFormatter(BaseMessageFormatter):
    """Enhanced grid formatter with customization options.

    Parameters
    ----------
    left_marker : str, default '» '
        Separator for the left side of the grid.
    right_marker : str, default ' «'
        Separator for the right side of the grid.
    overflow : str, default 'ellipsis'
        The behaviour expected from the Rich `Text` object when not enough space is
        available to render it.
    justify : str, default 'left'
        Text alignment to be passed to the Rich `Text` object.
    expand : bool, default True
        Flag for Rich `Table` that defines if the object should expand to fill the width
        of the terminal.
    """

    def __init__(
        self,
        left_marker: str = "» ",
        right_marker: str = " «",
        overflow: Literal["fold", "crop", "ellipsis", "ignore"] | None = "ellipsis",
        justify: Literal["default", "left", "center", "right", "full"] = "left",
        *,
        expand: bool = True,
    ) -> None:
        self.left_marker = left_marker
        self.right_marker = right_marker
        self.expand = expand
        self.overflow = overflow
        self.justify = justify

    def format_message(self, message: str) -> Table:
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
        grid = Table.grid(expand=self.expand)

        grid.add_column(justify="left", no_wrap=True)
        grid.add_column(justify=self.justify, ratio=1)
        grid.add_column(justify="center", no_wrap=True)

        grid_message = Text.from_markup(message, overflow=self.overflow)
        grid.add_row(self.left_marker, grid_message, self.right_marker)

        return grid


def style_renderer(style: str) -> Callable[[Text], Text]:
    """Add the option to specify `style` on a logger call for Rich to handle.

    Parameters
    ----------
    style : str
        A valid Rich style.
    """

    def highlighter(text: Text) -> Text:
        return Text(text.plain, style=style)

    return highlighter
