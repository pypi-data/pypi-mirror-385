"""A simple bytes file handler with locking and lazy open."""

from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any

from bear_dereth.files.base_file_handler import BaseFileHandler
from bear_dereth.files.file_lock import LockExclusive, LockShared

if TYPE_CHECKING:
    from pathlib import Path


class BytesFileHandler(BaseFileHandler[bytes]):
    """A simple bytes file handler with locking and lazy open.

    - Lazily opens the file on first use
    - Uses fcntl file locks for read/write sections
    - Provides read_bytes(), write_bytes(), clear(), and basic handle helpers
    """

    def __init__(self, file: str | Path, mode: str = "a+b", touch: bool = False) -> None:
        """Initialize the bytes file handler.

        Args:
            file: Path to the bytes file
            mode: File open mode (default: "a+b")
            touch: Whether to create the file if it doesn't exist (default: False)
        """
        super().__init__(file=file, mode=mode, touch=touch)

    def read(self, **kwargs) -> bytes:
        """Read the entire file (or up to n bytes) as bytes with a shared lock."""
        handle: IO[Any] | None = self.handle()
        if handle is None:
            raise ValueError("File handle is not available.")
        with LockShared(handle):
            handle.seek(0)
            data: bytes = handle.read(kwargs.pop("n", -1))
            return data

    def write(self, data: bytes, **kwargs) -> None:
        """Replace file contents with bytes using an exclusive lock."""
        handle: IO[Any] | None = self.handle()
        if handle is None:
            raise ValueError("File handle is not available.")
        with LockExclusive(handle):
            handle.seek(0)
            handle.truncate(0)
            handle.write(data)
            handle.flush()


# ruff: noqa: ARG002
