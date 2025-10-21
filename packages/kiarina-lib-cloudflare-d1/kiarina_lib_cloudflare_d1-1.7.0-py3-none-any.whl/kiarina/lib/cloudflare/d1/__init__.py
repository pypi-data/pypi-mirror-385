import logging
from importlib import import_module
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._sync.client import D1Client
    from ._sync.registry import create_d1_client
    from .settings import D1Settings, settings_manager

__version__ = version("kiarina-lib-cloudflare-d1")

__all__ = [
    "D1Client",
    "create_d1_client",
    "D1Settings",
    "settings_manager",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        # ._sync
        "D1Client": "._sync.client",
        "create_d1_client": "._sync.registry",
        # .settings
        "D1Settings": ".settings",
        "settings_manager": ".settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
