"""Formatter protocol definition for the logger system."""

import traceback
from typing import Any, Protocol, Self, overload

from bear_epoch_time import EpochTimestamp

from bear_dereth.logger.config.loggings import FormatterConfig
from bear_dereth.logger.records import LoggerRecord
from bear_dereth.logger.records.fmt import FormatCompiler
from bear_dereth.logger.records.time_helper import TimeHelper
from bear_dereth.typing_tools import LitFalse, LitTrue


class Formatter(Protocol):
    """A protocol for log message formatters.

    Formatters are responsible for transforming raw log data into formatted strings
    that can be consumed by handlers for output.
    """

    name: str = ""
    fmt: str
    datefmt: str
    exec_fmt: str
    time_helper: TimeHelper
    fmt_config: FormatterConfig
    _tmpl: FormatCompiler
    _exec_tmpl: FormatCompiler

    def __new__(cls, *args, **kwargs) -> Self:  # noqa: ARG004
        """Create a new instance of the formatter."""
        new: Self = super().__new__(cls)
        new.name = cls.__name__
        return new

    def __init__(
        self,
        config: FormatterConfig,
        fmt: str,
        datefmt: str,
        exec_fmt: str,
    ) -> None:
        """Initialize the formatter with an optional name and format templates.

        Args:
            fmt: Format template string
            datefmt: Optional date format string
            exec_fmt: Optional separate template for exception messages (falls back to fmt if not provided)
            config: LoggerConfig for default settings, extracted formatter configuration
        """
        self.fmt: str = fmt
        self.datefmt: str = datefmt
        self.time_helper: TimeHelper = TimeHelper(datefmt=self.datefmt)
        self.exec_fmt: str = exec_fmt
        self.fmt_config: FormatterConfig = config
        self._tmpl = FormatCompiler(self.fmt)
        self._exec_tmpl = FormatCompiler(self.exec_fmt)

    @overload
    def format(self, record: LoggerRecord, as_dict: LitTrue, **kwargs) -> dict: ...
    @overload
    def format(self, record: LoggerRecord, as_dict: LitFalse = False, **kwargs) -> str: ...

    def format(self, record: LoggerRecord, as_dict: bool = False, **kwargs) -> str | dict:
        """Format a log message into a string.

        Args:
            record(LoggerRecord): The log record to format
            **kwargs: Additional context data for formatting

        Returns:
            A formatted string ready for output by a handler
        """
        subs: dict[str, Any] = self._create_dict(record, **kwargs)
        if as_dict:
            return subs
        if LoggerRecord.has_exception(record.stack_info.exception):
            return self._exec_tmpl.compile(**subs)
        return self._tmpl.compile(**subs)

    def _parse_timestamp(self, timestamp: EpochTimestamp) -> str:
        """Parse a timestamp into a formatted string.

        Args:
            timestamp(EpochTimestamp): The timestamp to format

        Returns:
            A formatted timestamp string
        """
        return self.time_helper.timestamp(timestamp)

    def _parse_time(self, timestamp: EpochTimestamp) -> str:
        """Parse a time into a formatted string.

        Args:
            timestamp(EpochTimestamp): The timestamp to format

        Returns:
            A formatted time string
        """
        return self.time_helper.time(timestamp)

    def _parse_date(self, timestamp: EpochTimestamp) -> str:
        """Parse a date into a formatted string.

        Args:
            timestamp(EpochTimestamp): The timestamp to format

        Returns:
            A formatted date string
        """
        return self.time_helper.date(timestamp)

    def _parse_tz(self) -> str:
        """Parse a timezone into a formatted string.

        Args:
            timestamp(EpochTimestamp): The timestamp to format

        Returns:
            A formatted timezone string
        """
        return str(self.time_helper.tz)

    def _create_dict(self, record: LoggerRecord, **kwargs) -> dict[str, Any]:
        """Create a dictionary of log record attributes for formatting.

        Args:
            record(LoggerRecord): The log record to extract data from
            **kwargs: Additional context data to include
        Returns:
            A dictionary of log record attributes and additional context
        """
        data: dict[str, Any] = {
            "timestamp": self._parse_timestamp(record.timestamp),
            "time": self._parse_time(record.timestamp),
            "date": self._parse_date(record.timestamp),
            "tz": self._parse_tz(),
            "msg": str(record.msg),
            "level": record.level.name,
            "caller_function": record.stack_info.caller_function,
            "filename": record.stack_info.filename,
            "fullpath": record.stack_info.path,
            "relative_path": record.stack_info.relative_path,
            "python_path": record.stack_info.python_path,
            "line_number": record.stack_info.line_number,
            "code_line": record.stack_info.code_line,
            **kwargs,
        }
        if LoggerRecord.has_exception(record.stack_info.exception):
            e: Exception = record.stack_info.exception
            data.update(
                {
                    "exception": str(e),
                    "exception_class": type(e).__name__,
                    "exception_details": self._format_exception(e),
                }
            )
        return data

    def _format_exception(self, e: Exception) -> str:
        """Format exception details including stack trace if enabled.

        Args:
            exception(Exception): The exception to format
        Returns:
            A formatted string with exception details
        """
        if not self.fmt_config.include_stack_trace:
            return f"{type(e).__name__}: {e}"

        exception_lines: list[str] = traceback.format_exception(type(e), e, e.__traceback__)
        full_trace: str = "".join(exception_lines)

        if len(full_trace) > self.fmt_config.max_exception_length:
            truncated: str = full_trace[: self.fmt_config.max_exception_length]
            return f"{truncated}\n... (truncated at {self.fmt_config.max_exception_length} chars)"
        return full_trace.rstrip()
