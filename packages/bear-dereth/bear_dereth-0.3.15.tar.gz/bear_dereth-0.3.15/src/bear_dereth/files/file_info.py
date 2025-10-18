"""A dataclass to hold file metadata information."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from bear_dereth.constants import KILOBYTES, MEGABYTES
from bear_dereth.files.helpers import get_file_hash, touch as touch_file

if TYPE_CHECKING:
    from os import stat_result
    from pathlib import Path


@dataclass(slots=True, frozen=True)
class FileInfo:
    """Dataclass to hold file metadata information."""

    path: Path

    def __getattr__(self, item: str) -> Any:
        """Delegate attribute access to the underlying Path object."""
        return getattr(self.path, item)

    def touch(self, exist_ok: bool = True, create_file: bool = True) -> None:
        """Update the file's access and modification times, creating the file if it does not exist."""
        touch_file(self.path, exist_ok=exist_ok, create_file=create_file)

    @property
    def file_hash(self) -> str:
        """Get the SHA256 hash of the file."""
        return get_file_hash(self.path) if self.exists and self.is_file else ""

    @property
    def name(self) -> str:
        """Get the file name."""
        return self.path.name

    @property
    def ext(self) -> str:
        """Get the file extension."""
        return self.path.suffix.lstrip(".")

    @property
    def exists(self) -> bool:
        """Check if the file exists."""
        return self.path.exists()

    @property
    def is_file(self) -> bool:
        """Check if the path is a file."""
        return self.path.is_file() if self.exists else False

    @property
    def stat(self) -> stat_result | None:
        """Get the file's stat result."""
        if not self.exists:
            return None
        return self.path.stat()

    @property
    def size(self) -> int:
        """Get the file size in bytes."""
        return self.stat.st_size if self.stat is not None else 0

    @property
    def size_kb(self) -> float:
        """Get the file size in kilobytes."""
        return (self.stat.st_size / KILOBYTES) if self.stat is not None else 0.0

    @property
    def size_mb(self) -> float:
        """Get the file size in megabytes."""
        return (self.stat.st_size / MEGABYTES) if self.stat is not None else 0.0

    @property
    def created(self) -> float | None:
        """Get the file creation time as a timestamp."""
        from bear_dereth.platform_utils import OS, get_platform  # noqa: PLC0415

        platform: OS = get_platform()
        if platform is OS.DARWIN:
            return self.stat.st_birthtime if self.stat is not None else None
        if platform is OS.WINDOWS:
            return self.stat.st_ctime if self.stat is not None else None
        return self.stat.st_mtime if self.stat is not None else None

    @property
    def modified(self) -> float | None:
        """Get the file modification time as a timestamp."""
        return self.stat.st_mtime if self.stat is not None else None
