"""This is some terrible sinning that should not exist, don't look at it. It doesn't exist if you don't look at it."""

from __future__ import annotations

from typing import Literal, Self

from bear_dereth.rich_enums import IntValue as LogValue, RichIntEnum

EXCEPTION: Literal[50] = 50
FAILURE: Literal[45] = 45
ERROR: Literal[40] = 40
WARNING: Literal[30] = 30
WARN: Literal[30] = WARNING
INFO: Literal[20] = 20
SUCCESS: Literal[15] = 15
DEBUG: Literal[10] = 10
VERBOSE: Literal[5] = 5
NOTSET: Literal[0] = 0


class LogLevel(RichIntEnum):
    """Enumeration for logging levels."""

    NOTSET = LogValue(NOTSET, "NOTSET")
    VERBOSE = LogValue(VERBOSE, "VERBOSE")
    DEBUG = LogValue(DEBUG, "DEBUG")
    INFO = LogValue(INFO, "INFO")
    WARNING = LogValue(WARNING, "WARNING")
    ERROR = LogValue(ERROR, "ERROR")
    FAILURE = LogValue(FAILURE, "FAILURE")
    SUCCESS = LogValue(SUCCESS, "SUCCESS")
    EXCEPTION = LogValue(EXCEPTION, "EXCEPTION")
    INVALID_LEVEL = LogValue(999, "INVALID_LEVEL")

    @classmethod
    def level_to_name(cls, level: int | str | Self) -> str:
        """Get the name of a logging level."""
        return LogLevel.get(level, default=LogLevel.INVALID_LEVEL).name

    @classmethod
    def name_to_level(cls, name: str | Self) -> int:
        """Get the numeric value of a logging level by its name."""
        return LogLevel.get(name, default=LogLevel.INVALID_LEVEL).value
