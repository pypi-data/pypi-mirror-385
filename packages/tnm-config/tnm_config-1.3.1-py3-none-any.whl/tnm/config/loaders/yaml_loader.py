from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from ._base import BaseLoader
from .._utils import _cast_env_value, _resolve_node, _resolve_filesystem_path
from ..errors import ConfigError

_is_yaml_installed = False
try:
    import yaml

    _is_yaml_installed = True
except (ImportError, ModuleNotFoundError):
    ...


class YAMLLoader(BaseLoader):
    def load(
        self,
        path: Path,
        *,
        project_root_callback: Callable[[], Path | str] | None = None,
    ) -> Any:
        if not _is_yaml_installed:
            raise ConfigError(
                "PyYAML is required to load YAML files. Install tnm-config[yaml]."
            )

        def _env_constructor(loader, node):
            values = loader.construct_sequence(node)
            default = values[2] if len(values) >= 3 else None
            return _cast_env_value(values[0], values[1], default)

        def _path_constructor(loader, node):
            if isinstance(node, yaml.nodes.ScalarNode):
                raw = loader.construct_scalar(node)
                return _resolve_filesystem_path(
                    raw, project_root_callback=project_root_callback
                )

            if isinstance(node, yaml.nodes.SequenceNode):
                parts = loader.construct_sequence(node)
                try:
                    combined = str(Path(parts[0]))
                except TypeError as e:
                    raise ConfigError(
                        "!path sequence must contain path segments (strings)"
                    ) from e

                return _resolve_filesystem_path(
                    combined, project_root_callback=project_root_callback
                )

            raise ConfigError(
                "!path must be a scalar or sequence (list) of path segments"
            )

        yaml.SafeLoader.add_constructor("!env", _env_constructor)
        yaml.SafeLoader.add_constructor("!path", _path_constructor)

        try:
            with path.open("r", encoding="utf-8") as fh:
                content = yaml.safe_load(fh)
        except Exception as exc:
            raise ConfigError(f"Failed to parse YAML config '{path}': {exc}") from exc

        return _resolve_node(content, project_root_callback=project_root_callback)
