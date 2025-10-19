"""Simple text file handler for line-agnostic IO with locking.

This is a minimal, reusable file handler intended for formats like
JSON (full-text) or general text. It provides safe read_text and
write_text operations with file locking and lazy handle management.

Note: For JSONL (line-oriented) use JSONLFilehandler, which provides
specialized iter/line APIs.
"""

from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any

from bear_dereth.files.base_file_handler import BaseFileHandler
from bear_dereth.files.file_lock import LockExclusive, LockShared

if TYPE_CHECKING:
    from pathlib import Path


class TextFileHandler(BaseFileHandler[str]):
    """A simple text file handler with locking and lazy open.

    - Lazily opens the file on first use
    - Uses fcntl file locks for read/write sections
    - Provides read_text(), write_text(), clear(), and basic handle helpers
    """

    def __init__(self, file: str | Path, mode: str = "a+", encoding: str = "utf-8", touch: bool = False) -> None:
        """Initialize the text file handler.

        Args:
            file: Path to the text file
            mode: File open mode (default: "a+")
            encoding: File encoding (default: "utf-8")
            touch: Whether to create the file if it doesn't exist (default: False)
        """
        super().__init__(file=file, mode=mode, encoding=encoding, touch=touch)

    def read(self, **kwargs) -> str:
        """Read the entire file (or up to n chars) as text with a shared lock."""
        handle: IO[Any] | None = self.handle()
        if handle is None:
            raise ValueError("File handle is not available.")
        with LockShared(handle):
            handle.seek(0)
            data: str = handle.read(kwargs.pop("n", -1))
            return data

    def write(self, data: str, **kwargs) -> None:
        """Replace file contents with text using an exclusive lock."""
        handle: IO[Any] | None = self.handle()
        if handle is None:
            raise ValueError("File handle is not available.")
        with LockExclusive(handle):
            handle.seek(0)
            handle.truncate(0)
            handle.write(data)
            handle.flush()


# ruff: noqa: ARG002
