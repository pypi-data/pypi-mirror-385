import re
import tempfile
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from . import get_config
from ._typeguard import typechecked
from .errors import EnvVarNotSetError, InvalidURLError, ConfigError

_TOKEN_RE = re.compile(r"(%\s*(?P<t1>[A-Za-z_]+)\s*%|\{\{\s*(?P<t2>[A-Za-z_]+)\s*}})")


def _apply_preserved_tokens(
    s: str, project_root_callback: Callable[[], Path | str] | None
) -> str:
    """
    Replace preserved tokens in a string with actual paths.
    """

    def _replace(m: re.Match) -> str:
        token = (m.group("t1") or m.group("t2") or "").strip().lower()
        if token in ("project_root", "project_dir", "project"):
            root = _get_project_root_from_callable(project_root_callback)
            return str(root)
        if token in ("home", "user_home"):
            return str(Path.home())
        if token in ("user", "username"):
            return str(Path.home())
        if token in ("temp", "temp_dir"):
            return str(Path(tempfile.gettempdir()))
        raise ConfigError(f"Unknown token {token!r} from {s!r}")

    return _TOKEN_RE.sub(_replace, s)


def _cast_env_value(var_name: str, type_hint: str, default: Any) -> Any:
    """
    Cast environment variable using type_hint.
    :raises EnvVarNotSetError: if missing and default is None.
    :raises InvalidURLError: on invalid input.
    :raises ValueError: on invalid input.
    """
    val: str | None = get_config(key=var_name, default=None)
    if val is None:
        if default is not None:
            return _match_type_hint(type_hint, default)
        raise EnvVarNotSetError(f"Environment variable '{var_name}' not set")

    return _match_type_hint(type_hint=type_hint, val=val)


def _match_type_hint(type_hint: str, val: Any):
    match type_hint:
        case "url":
            parsed = urlparse(val)
            if not parsed.scheme or not parsed.netloc:
                raise InvalidURLError(f"Provided URL '{val}' is invalid.")
            return val
        case "str":
            return val
        case "int":
            return int(val)
        case "float":
            return float(val)
        case "bool":
            v = str(val).lower()
            if v in ("1", "true", "yes", "y", "on"):
                return True
            if v in ("0", "false", "no", "n", "off"):
                return False
            raise ValueError(f"Cannot cast '{val}' to bool")
        case hint if hint.startswith("list:str"):
            return [item.strip() for item in str(val).split(",") if item.strip()]
        case hint if hint.startswith("list:url"):
            valid = []
            for item in str(val).split(","):
                parsed = urlparse(item.strip())
                if not parsed.scheme or not parsed.netloc:
                    raise InvalidURLError(
                        f"The provided URL {item!r} in list {val!r} is invalid."
                    )
                valid.append(item.strip())
            return valid
        case _:
            raise ValueError(f"Unsupported env type hint: {type_hint!r}")


@typechecked
def _get_project_root_from_callable(
    project_root_callback: Callable[[], Path | str] | None,
) -> Path:
    """Return a resolved Path from the provided callable."""
    if not project_root_callback:
        raise ConfigError(
            "'project_root_callback' is required for !path with project_relative=True"
        )

    try:
        p = project_root_callback()
    except Exception as exc:
        raise ConfigError(
            f"'project_root_callback' raised an exception: {str(exc)}"
        ) from exc
    if not isinstance(p, Path):
        p = Path(p)

    p = p.resolve()

    if not p.is_dir():
        raise ConfigError(f"'project_root_callback' is not a directory: {p}")

    return p


def _resolve_filesystem_path(
    value: Any,
    project_root_callback: Callable[[], Path | str] | None = None,
) -> Any:
    """
    Resolve filesystem paths for values that are intended as paths.
    """
    if isinstance(value, list):
        return [
            _resolve_filesystem_path(item, project_root_callback=project_root_callback)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            k: _resolve_filesystem_path(v, project_root_callback=project_root_callback)
            for k, v in value.items()
        }

    if isinstance(value, str):
        if _TOKEN_RE.search(value):
            replaced = _apply_preserved_tokens(value, project_root_callback)
            p = Path(replaced)
            if p.is_absolute():
                return str(p.resolve())
            root = _get_project_root_from_callable(project_root_callback)
            return str((root / replaced).resolve())

        return value

    return value


def _resolve_node(
    node: Any, project_root_callback: Callable[[], Path | str] | None = None
) -> Any:
    """
    Recursively resolve special markers.

    Important: do not attempt to treat every string as a path. Strings are only
    path-resolved when they contain preserved tokens (e.g. %project_root% or {{home}})
    or when the loader explicitly provided a path marker/dict (e.g. __path__ / !path).
    """

    if isinstance(node, list):
        return [
            _resolve_node(item, project_root_callback=project_root_callback)
            for item in node
        ]

    if isinstance(node, dict):
        return {
            k: _resolve_node(v, project_root_callback=project_root_callback)
            for k, v in node.items()
        }

    if isinstance(node, str):
        if _TOKEN_RE.search(node):
            return _resolve_filesystem_path(
                node, project_root_callback=project_root_callback
            )
        return node

    return node
