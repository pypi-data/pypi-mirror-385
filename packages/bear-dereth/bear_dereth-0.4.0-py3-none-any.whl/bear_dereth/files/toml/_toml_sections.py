"""A helper class for TOML sections for dot notation parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bear_dereth.data_structs.stacks import SimpleStack as Stack

if TYPE_CHECKING:
    from bear_dereth.files.toml.file_handler import TomlData


class TomlSection:  # pragma: no cover # Not really using this yet
    """Fluent accessor for TOML data with dot notation."""

    def __init__(self, data: TomlData, path: list[str] | None = None) -> None:
        """Initialize with the full TOML data."""
        self._data = data
        self._path: list[str] = path or []
        self._value_cache: dict[str, Any] = {}
        self._dot_map: dict[str, Any] = {}

    @property
    def dot_map(self) -> dict[str, Any]:
        """Map out all possible paths for fast lookup."""
        if not self._dot_map:
            stack: Stack[tuple[list, TomlData]] = Stack(([], self._data))

            while stack:
                current_path, current_value = stack.pop()
                if isinstance(current_value, dict):
                    for k, v in current_value.items():
                        stack.push(([*current_path, k], v))
                else:
                    self._dot_map[".".join(current_path)] = current_value
        return self._dot_map

    def __getattr__(self, key: str) -> Any:
        """Access a sub-key, returning a new TomlSection."""
        new_section: TomlSection = TomlSection(self._data, [*self._path, key])
        result: TomlData | None = new_section._navigate()
        return result if result is not None else new_section

    def __setattr__(self, key: str, value: Any) -> None:
        """Set attribute normally, except for _data and _path."""
        if key in {"_data", "_path", "_value_cache", "_dot_map"}:
            super().__setattr__(key, value)
        else:
            current = self._data
            for part in self._path:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[key] = value

            self._value_cache.clear()
            self._dot_map.clear()

    def __getitem__(self, key: str) -> Any:
        """Allow bracket notation: section['key']"""
        return self.__getattr__(key)

    def _navigate(self) -> TomlData | None:
        path_str: str = ".".join(self._path)
        if path_str not in self._value_cache:
            self._value_cache[path_str] = self.dot_map.get(path_str)
        return self._value_cache[path_str]

    def get(self, key: str, default: Any = None) -> TomlData | None:
        """Resolve the path and return value."""
        return self.__getattr__(key) or default


if __name__ == "__main__":
    sample_toml: str = """
    [project]
    name = "bear-dereth"
    description = "A set of common tools for various bear projects."
    dynamic = ["version"]
    authors = [{name = "chaz", email = "bright.lid5647@fastmail.com"}]
    readme = "README.md"
    requires-python = ">=3.12"
    keywords = []
    dependencies = [
        "bear-epoch-time>=1.2.2",
        "distro>=1.9.0",
        "pydantic>=2.11.5",
        "pyyaml>=6.0.3",
        "rich>=14.1.0",
        "singleton-base>=1.2.3",
        "tomlkit>=0.13.3",
    ]

    [project.scripts]
    bear-dereth = "bear_dereth._internal.cli:main"

    [build-system]
    requires = ["hatchling", "uv-dynamic-versioning"]
    build-backend = "hatchling.build"
    """
    from tomllib import loads

    parsed_data: TomlData = loads(sample_toml)
    toml_section: TomlSection = TomlSection(data=parsed_data)

    print(toml_section.project.name)  # Outputs: bear-dereth
    toml_section.project.name = "new-name"
    print(toml_section.project.name)  # Outputs: new-name
    print(toml_section.dot_map)
