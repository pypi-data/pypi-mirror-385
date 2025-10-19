# from __future__ import annotations
#
# import tomllib  # type: ignore
# from pathlib import Path
# from typing import Any, Callable
#
# from ._base import BaseLoader
# from .._utils import _cast_env_value, _resolve_project_path
# from ..errors import ConfigError
#
#
# class TomlLoader(BaseLoader):
#     def _normalize_node(
#         self, node: Any, project_root_callback: Callable[[], Path | str] | None
#     ):
#         if isinstance(node, dict):
#             if "__env__" in node and isinstance(node["__env__"], list):
#                 val = node["__env__"]
#                 default = val[2] if len(val) >= 3 else None
#                 return _cast_env_value(val[0], val[1], default)
#             if "__path__" in node and isinstance(node["__path__"], dict):
#                 data = node["__path__"]
#                 return _resolve_project_path(
#                     data["value"],
#                     project_root_callback=project_root_callback,
#                     project_relative=data.get("project_relative", True),
#                 )
#
#             return {
#                 k: self._normalize_node(v, project_root_callback)
#                 for k, v in node.items()
#             }
#         if isinstance(node, list):
#             return [self._normalize_node(i, project_root_callback) for i in node]
#
#         if isinstance(node, str):
#             return _resolve_project_path(
#                 node,
#                 project_root_callback=project_root_callback,
#                 project_relative=False,
#             )
#         return node
#
#     def load(
#         self,
#         path: Path,
#         *,
#         project_root_callback: Callable[[], Path | str] | None = None,
#     ) -> Any:
#         if tomllib is None:
#             raise ConfigError(
#                 "TOML support requires Python 3.11+ (tomllib) or the 'tomli' package. "
#                 "Install with `pip install tomli` or use Python 3.11+."
#             )
#
#         try:
#             with path.open("rb") as fh:
#                 content = tomllib.load(fh)
#         except Exception as exc:
#             raise ConfigError(f"Failed to parse TOML config '{path}': {exc}") from exc
#
#         return self._normalize_node(
#             content, project_root_callback=project_root_callback
#         )
