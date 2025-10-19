"""In-memory log recording utilities for Python's logging framework.

This module provides a `RecordingHandler` and helper methods to
dynamically attach and detach in-memory log recorders to standard
`logging.Logger` instances. It allows recording log output programmatically
for testing, debugging, or analysis without relying on files or streams.

Example:
    >>> import logging
    >>> import emtest.log_recording
    >>> logger = logging.getLogger("demo")
    >>> logger.setLevel(logging.INFO)
    >>> logger.start_recording()  # Start recording logs
    >>> logger.info("Hello world")
    >>> logs = logger.get_recording()
    >>> print(logs)
    ['2025-10-18 10:00:00,000 [INFO] Hello world']
    >>> logger.stop_recording()  # Stop and remove recorder
"""

import logging


class RecordingHandler(logging.Handler):
    """A logging handler that buffers formatted log records in memory.

    This handler captures each emitted log record, formats it,
    and stores the resulting string in an internal list.
    It is useful for unit tests or scenarios where log output
    needs to be inspected programmatically.

    Attributes:
        formatter (logging.Formatter): The formatter used to format log messages.
        _records (list[str]): Internal buffer of recorded log messages.
    """

    def __init__(self, formatter: logging.Formatter):
        """Initialize the handler with a specific formatter.

        Args:
            formatter (logging.Formatter): Formatter to apply to each log record.
        """
        super().__init__()
        self.formatter = formatter
        self._records: list[str] = []

    def emit(self, record: logging.LogRecord):
        """Store a formatted log record in the internal buffer.

        Args:
            record (logging.LogRecord): The log record to handle.
        """
        self._records.append(self.format(record))

    def get_records(self) -> list[str]:
        """Retrieve the recorded log messages.

        Returns:
            list[str]: A copy of the list of formatted log messages.
        """
        return list(self._records)

    def clear(self):
        """Clear all recorded log messages from the buffer."""
        self._records.clear()


def start_recording(self: logging.Logger, name: str | None = None):
    """Start recording logs to a named recorder.

    This function dynamically attaches a `RecordingHandler` to the logger.
    If a recorder with the given name already exists, it does nothing.

    The recorder uses the formatter from the first existing handler
    if available, or falls back to a default formatter.

    Args:
        self (logging.Logger): The logger instance.
        name (str | None): Optional name of the recorder. Defaults to `"__default__"`.

    Example:
        >>> logger.start_recording("test")
        >>> logger.info("Message")
    """
    if name is None:
        name = "__default__"

    # Ensure the logger has a dict of recording handlers attached
    if not hasattr(self, "_recording_handlers"):
        self._recording_handlers = {}
    if name in self._recording_handlers:
        return  # already recording under this name

    # Use same formatter as first handler, or fallback
    if self.handlers:
        formatter = self.handlers[0].formatter
    else:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    handler = RecordingHandler(formatter)
    self.addHandler(handler)
    self._recording_handlers.update({name: handler})


def stop_recording(self: logging.Logger, name: str | None = None):
    """Stop and remove a named recorder from the logger.

    If no recorder exists for the given name, the function does nothing.

    Args:
        self (logging.Logger): The logger instance.
        name (str | None): Optional name of the recorder to stop.
            Defaults to `"__default__"`.

    Example:
        >>> logger.stop_recording("test")
    """
    if name is None:
        name = "__default__"

    handler = self._recording_handlers.get(name, None)
    if handler:
        self.removeHandler(handler)


def get_recording(self: logging.Logger, name: str | None = None) -> list[str]:
    """Retrieve the recorded log messages for a named recorder.

    Args:
        self (logging.Logger): The logger instance.
        name (str | None): Optional name of the recorder. Defaults to `"__default__"`.

    Returns:
        list[str]: A list of formatted log messages recorded so far.
            Returns an empty list if no handler is found for the name.

    Raises:
        KeyError: If the recorder with the specified name does not exist.

    Example:
        >>> messages = logger.get_recording("test")
        >>> print(messages)
    """
    if name is None:
        name = "__default__"

    handler = self._recording_handlers[name]
    return handler.get_records() if handler else []


# Monkey-patch Logger with recording methods
logging.Logger.start_recording = start_recording
logging.Logger.stop_recording = stop_recording
logging.Logger.get_recording = get_recording
