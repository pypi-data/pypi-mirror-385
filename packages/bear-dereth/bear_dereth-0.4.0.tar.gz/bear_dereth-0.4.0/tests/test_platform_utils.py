from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import pytest

from bear_dereth.platform_utils import (
    DARWIN,
    LINUX,
    WINDOWS,
    get_platform,
    is_linux,
    is_macos,
    is_windows,
)


@pytest.fixture(autouse=True)
def clear_platform_cache() -> Generator[None, Any]:
    get_platform.cache_clear()  # Clear the cache before each test
    yield
    get_platform.cache_clear()  # Clear the cache after each test


@patch("platform.system", return_value="Darwin")
def test_macos(mock_system):
    assert get_platform() == DARWIN
    assert is_macos()
    assert not is_windows()
    assert not is_linux()


@patch("platform.system", return_value="Windows")
def test_windows(mock_system) -> None:
    assert get_platform() == WINDOWS
    assert is_windows()
    assert not is_macos()
    assert not is_linux()


@patch("platform.system", return_value="Linux")
def test_linux(mock_system) -> None:
    assert get_platform() == LINUX
    assert is_linux()
    assert not is_macos()
    assert not is_windows()


@patch("platform.system", return_value="FakeOS")
def test_other(mock_system) -> None:
    assert get_platform() == "Other"
    assert not is_macos()
    assert not is_windows()
    assert not is_linux()
