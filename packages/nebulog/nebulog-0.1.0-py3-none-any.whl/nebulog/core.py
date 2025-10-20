"""Default values and enumerations."""

from enum import Enum

import logging
from loguru._logger import Core

for level in Core().levels.values():
    logging.addLevelName(level.no, level.name)

LOGGING_LEVELS = logging._nameToLevel
LOG_LEVEL_JUSTIFICATION = max(len(i) for i in LOGGING_LEVELS)

DEFAULT_TIME_FORMAT = (
    "[b]⟪[/] [yellow]%Y.%m.%d[/yellow] [dim]%H:%M[green][b]:%S[/dim][/green] ⟫[/]"
)


class TimeDisplayMode(Enum):
    """An enumeration to control how the log timestamp is rendered."""

    SEPARATE_LINE = "separate"
    INLINE_LEFT = "left"
    INLINE_RIGHT = "right"
    HIDDEN = "hidden"


class TracebackMode(Enum):
    """An enumeration to control whether exceptions tracebacks are shown or not."""

    SUPPRESS = "suppress"
    RICH = "rich"
