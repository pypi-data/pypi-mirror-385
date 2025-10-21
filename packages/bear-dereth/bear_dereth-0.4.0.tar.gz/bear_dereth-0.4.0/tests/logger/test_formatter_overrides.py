"""Tests for per-handler and global formatter overrides."""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from bear_dereth.logger.common.log_level import LogLevel
from bear_dereth.logger.config import LoggerConfig
from bear_dereth.logger.config.di import get_config_manager, get_default_config
from bear_dereth.logger.handlers.console_handler import ConsoleHandler
from bear_dereth.logger.handlers.file_handler import FileHandler
from bear_dereth.logger.records import LoggerRecord, StackInfo

if TYPE_CHECKING:
    from pathlib import Path


def test_console_handler_fmt_override() -> None:
    buf = StringIO()
    fmt = "$level $filename:$line_number $msg"

    config_manager = get_config_manager(program_name="logger", env="test")
    cfg: LoggerConfig = get_default_config(config_manager)
    handler: ConsoleHandler[StringIO] = ConsoleHandler(file=buf, fmt=fmt, config=cfg)

    stack: StackInfo = StackInfo.from_current_stack()
    record = LoggerRecord(msg="hello", style="info", level=LogLevel.INFO, stack_info=stack)
    handler.emit(record)

    out = buf.getvalue()
    assert "INFO" in out
    assert "test_formatter_overrides.py" in out
    assert "hello" in out


def test_file_handler_fmt_override(tmp_path: Path) -> None:
    log_file = tmp_path / "fmt.log"
    fmt = "$level $filename:$line_number $msg"
    handler = FileHandler(file_path=log_file, fmt=fmt)

    stack: StackInfo = StackInfo.from_current_stack()
    record = LoggerRecord(msg="world", style="info", level=LogLevel.INFO, stack_info=stack)
    handler.emit(record)

    handler.close()
    text = log_file.read_text()
    # Remove whitespace/line breaks for easier matching
    text_normalized = "".join(text.split())
    assert "INFO" in text
    assert "test_formatter_overrides.py" in text_normalized or "formatter_overrides.py" in text
    assert "world" in text
