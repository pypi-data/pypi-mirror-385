"""Logger record definition."""

from __future__ import annotations

from typing import Any, TypeGuard

from bear_epoch_time import EpochTimestamp
from pydantic import Field, field_serializer, field_validator

from bear_dereth.data_structs.freezing import FrozenModel
from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.records.stack_info import StackInfo


class LoggerRecord(FrozenModel):
    """A message container for queue processing."""

    msg: object
    stack_info: StackInfo
    style: str
    level: LogLevel = Field(default=LogLevel.DEBUG)
    timestamp: EpochTimestamp = Field(default_factory=EpochTimestamp.now, exclude=True)
    args: tuple[Any, ...] | None = Field(default=None, repr=False)
    kwargs: dict[str, Any] | None = Field(default=None, repr=False)

    @field_validator("stack_info", mode="before")
    @classmethod
    def validate_stack_info(cls, v: StackInfo | dict | None) -> StackInfo | None:
        """Ensure stack_info is a StackInfo instance."""
        if v is None or isinstance(v, StackInfo):
            return v
        return StackInfo.model_validate(v)

    @field_serializer("msg")
    def serialize_msg(self, msg: object) -> str:
        """Serialize the msg field for output."""
        return str(msg)

    @field_serializer("level")
    def serialize_level(self, level: LogLevel) -> str:
        """Serialize the level field for output."""
        return level.name

    @staticmethod
    def has_exception(e: Exception | None) -> TypeGuard[Exception]:
        """Check if an exception is present.

        Args:
            e: The exception to check
        Returns:
            True if an exception is present, False otherwise
        """
        return e is not None
