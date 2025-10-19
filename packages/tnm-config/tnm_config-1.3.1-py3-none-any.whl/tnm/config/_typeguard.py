from __future__ import annotations

import importlib
import logging
from functools import wraps
from typing import Callable, Any, TypeVar, overload, Optional

from .errors import ConfigError

T_CallableOrType = TypeVar("T_CallableOrType", bound=Callable[..., Any])

logger = logging.getLogger(__name__)

_is_tg_installed = True
_tg = None
try:
    _tg = importlib.import_module("typeguard")
    _typechecked = getattr(_tg, "typechecked", None)
    _TypeCheckError = getattr(_tg, "TypeCheckError", None)
except Exception:
    _is_tg_installed = False


if _is_tg_installed:
    try:
        setattr(_tg, "TypeCheckError", ConfigError)
        try:
            _checkers = importlib.import_module("typeguard._checkers")
            setattr(_checkers, "TypeCheckError", ConfigError)
        except Exception:
            logger.debug(
                "typeguard._checkers not patched (not present or inaccessible)."
            )
    except Exception:
        logger.debug(
            "Could not alias typeguard.TypeCheckError to ConfigError; adapter will still catch errors."
        )


def _wrap_decorated(
    func: T_CallableOrType, decorated: Callable[..., Any]
) -> T_CallableOrType:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return decorated(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, ConfigError):
                raise exc

            if _TypeCheckError is not None and isinstance(exc, _TypeCheckError):
                raise ConfigError(
                    f"type validation failed for {func.__name__}: {str(exc)}"
                ) from exc
            raise

    return wrapper  # type: ignore[return-value]


@overload
def typechecked(
    func: None = None,
) -> Callable[[T_CallableOrType], T_CallableOrType]: ...


@overload
def typechecked(func: T_CallableOrType) -> T_CallableOrType: ...


def typechecked(func: Optional[T_CallableOrType] = None) -> Any:
    if _typechecked is None:

        def identity_decorator(f: T_CallableOrType) -> T_CallableOrType:
            return f

        if func is None:
            return identity_decorator  # used as @typechecked()
        return identity_decorator(func)

    # If used as @typechecked without parentheses
    if func is not None:
        try:
            decorated = _typechecked(func)
        except Exception as exc:
            raise ConfigError(
                f"failed to enable runtime type checks for {func.__name__}: {str(exc)}"
            ) from exc
        return _wrap_decorated(func, decorated)

    # Used as @typechecked()
    def _inner(fn: T_CallableOrType) -> T_CallableOrType:
        try:
            _decorated = _typechecked(fn)
        except Exception as ex:
            raise ConfigError(
                f"failed to enable runtime type checks for {fn.__name__}: {str(ex)}"
            ) from ex
        return _wrap_decorated(fn, _decorated)

    return _inner
