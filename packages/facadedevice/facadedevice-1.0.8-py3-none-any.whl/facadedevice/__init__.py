"""Provide a proxy device to subclass."""

from facadedevice.device import Facade, TimedFacade
from facadedevice.graph import triplet
from facadedevice.objects import (
    combined_attribute,
    local_attribute,
    logical_attribute,
    proxy_attribute,
    proxy_command,
    state_attribute,
)

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0+unknown"

__all__ = [
    "Facade",
    "TimedFacade",
    "triplet",
    "proxy_attribute",
    "local_attribute",
    "logical_attribute",
    "state_attribute",
    "proxy_command",
    "combined_attribute",
]
