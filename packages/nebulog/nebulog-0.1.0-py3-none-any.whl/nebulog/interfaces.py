"""Protocols and interfaces defining expected renderer behaviour."""

from typing import Protocol, runtime_checkable

from abc import ABC, abstractmethod

from rich.console import ConsoleRenderable


@runtime_checkable
class MessageFormatter(Protocol):
    """Protocol for message formatters."""

    def format_message(self, message: str) -> ConsoleRenderable:
        """Format a log message."""
        ...


class BaseMessageFormatter(ABC):
    """Abstract base class for message formatters."""

    @abstractmethod
    def format_message(self, message: str) -> ConsoleRenderable:
        """Format the message with access to the full log record."""
        pass

    def __call__(  # noqa: D102
        self, message: str
    ) -> ConsoleRenderable:
        return self.format_message(message)


class TimeRenderer(ABC):
    """Abstract base class for timestamp formatters."""

    @abstractmethod
    def render_time(self, log_time: str) -> ConsoleRenderable | None:
        """Render time component. Return None if time should be inline."""
        pass
