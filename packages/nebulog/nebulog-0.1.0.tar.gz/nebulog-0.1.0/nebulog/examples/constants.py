"""Fixed objects for usage with Nebulog sample code."""

from rich.console import Console
from rich.theme import Theme

SAMPLE_CONSOLE = Console(
    theme=Theme(
        {
            "logging.level.trace": "bright_black",
            "logging.level.debug": "bright_cyan",
            "logging.level.success": "green",
            "regex.major": "bold green",
            "regex.minor": "bold blue",
            "regex.patch": "yellow",
            "regex.prerelease": "dim red",
            "regex.build": "dim",
        }
    )
)
