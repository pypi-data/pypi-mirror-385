"""Nebulog renderers for log timestamps."""

from typing import Literal

from rich.console import ConsoleRenderable
from rich.rule import Rule
from rich.text import Text

from nebulog.interfaces import TimeRenderer


class SeparateLineTimeRenderer(TimeRenderer):
    """Render the timestamp in a separate line via a `Rule` ConsoleRenderable.

    Parameters
    ----------
    style : str
        Rich style for the `Rule` renderable.
    align : str, default 'left'
        Text alignment to be passed to the `Rule` renderable.
    """

    def __init__(
        self, style: str = "dim", align: Literal["left", "center", "right"] = "left"
    ) -> None:
        self.style = style
        self.align = align

    def render_time(self, log_time: str) -> ConsoleRenderable:
        """Render the formatted timestamp with a `Rule` renderable.

        Parameters
        ----------
        log_time : str
            String for `strftime` that formats the time.
        """
        time_text = Text.from_markup(log_time)

        return Rule(time_text, align=self.align, style=self.style)


class InlineTimeRenderer(TimeRenderer):
    """Render the timestamp inline with the log call."""

    def __init__(self):
        pass

    def render_time(self, log_time: str) -> Text:
        """Render the formatted timestamp with a `Text` renderable.

        Parameters
        ----------
        log_time : str
            String for `strftime` that formats the time.
        """
        return Text.from_markup(log_time)


class HiddenTimeRenderer(TimeRenderer):
    """Provide an interface to not render the timestamp."""

    def __init__(self):  # Explicit constructor for consistency
        pass

    def render_time(self, log_time: str) -> None:  # noqa: ARG002
        """Render the formatted timestamp with a `Text` renderable.

        Parameters
        ----------
        log_time : str
            String for `strftime` that formats the time.
        """
        return
