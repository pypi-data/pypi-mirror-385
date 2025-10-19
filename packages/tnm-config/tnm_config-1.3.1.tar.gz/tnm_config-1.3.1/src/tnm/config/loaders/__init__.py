from __future__ import annotations

import logging
from typing import Callable, Dict

from ._base import BaseLoader
from .json_loader import JSONLoader
from .xml_loader import XMLLoader
from .yaml_loader import YAMLLoader
from .._typeguard import typechecked
from ..errors import ConfigError

logger = logging.getLogger(__name__)

LoaderFactory = Callable[[], BaseLoader]
_registry: Dict[str, LoaderFactory] = {}


def _normalize_loader_id(id: str):
    id = id.strip(".")

    return f".{id}"


@typechecked
def register_loader(suffix: str, factory: LoaderFactory):
    suffix = _normalize_loader_id(suffix)

    if suffix not in _registry:
        _registry.update({suffix: factory})


def get_loader(suffix: str):
    keys = sorted(_registry.keys())

    if not keys:
        raise ConfigError("No loaders have been registered. Yet.")

    suffix = _normalize_loader_id(suffix)
    loader_factory = _registry.get(_normalize_loader_id(suffix), None)

    if not loader_factory:
        raise ConfigError(
            f"No supported loader found for the suffix {suffix!r}. Supported suffixes are {', '.join(keys)!r}"
        )

    return loader_factory()


@typechecked
def _register_built_in_loaders(suffixes: list[str], loader: LoaderFactory):
    for suffix in suffixes:
        register_loader(suffix, loader)


_register_built_in_loaders([".yaml", ".yml"], lambda: YAMLLoader())
_register_built_in_loaders([".json"], lambda: JSONLoader())
_register_built_in_loaders([".xml"], lambda: XMLLoader())

__all__ = ["get_loader", "register_loader", "BaseLoader"]
