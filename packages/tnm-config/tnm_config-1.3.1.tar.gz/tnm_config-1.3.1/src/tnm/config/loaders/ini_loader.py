# from __future__ import annotations
#
# import configparser
# import json
# from pathlib import Path
# from typing import Any, Callable, Dict
#
# from ._base import BaseLoader
# from .._utils import _resolve_node, _cast_env_value, _resolve_project_path
# from ..errors import ConfigError
#
#
# class IniLoader(BaseLoader):
#
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
#     @staticmethod
#     def _try_parse_marker_string(s: str):
#         s_strip = s.strip()
#
#         if s_strip.startswith("{") or s_strip.startswith("["):
#             try:
#                 return json.loads(s_strip)
#             except Exception:
#                 pass
#         if s_strip.startswith("__env__::"):
#             parts = s_strip.split("::")
#             return {"__env__": parts[1:]}
#         if s_strip.startswith("__path__::"):
#             parts = s_strip.split("::")
#             pr = parts[2].lower() in ("1", "true", "yes") if len(parts) > 2 else True
#             return {"__path__": {"value": parts[1], "project_relative": pr}}
#         return s
#
#     def load(
#         self,
#         path: Path,
#         *,
#         project_root_callback: Callable[[], Path | str] | None = None,
#     ) -> Any:
#         """
#         Parse an INI file into a dict-of-dicts and run normalization.
#         """
#         try:
#             parser = configparser.ConfigParser(interpolation=None)
#
#             parser.optionxform = str
#             parser.read(path, encoding="utf-8")
#
#             content: Dict[str, Dict[str, Any]] = {}
#             for section in parser.sections():
#                 items = {}
#                 for key, raw_val in parser.items(section):
#                     val: Any = raw_val
#
#                     s = raw_val.strip()
#                     if (
#                         s.startswith("{")
#                         or s.startswith("[")
#                         or s.startswith('"')
#                         or s in ("null", "true", "false")
#                         or s[0].isdigit()
#                         or (s.startswith("-") and s[1:].isdigit())
#                     ):
#                         try:
#                             val = json.loads(raw_val)
#                         except Exception:
#                             val = raw_val
#                     items[key] = val
#                 content[section] = items
#
#         except Exception as exc:
#             raise ConfigError(f"Failed to parse INI config '{path}': {exc}") from exc
#
#         return self._normalize_node(
#             content, project_root_callback=project_root_callback
#         )
