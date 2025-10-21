import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._async.client import D1Client
    from ._async.registry import create_d1_client
    from .settings import D1Settings, settings_manager

__all__ = [
    # ._async
    "D1Client",
    "create_d1_client",
    # .settings
    "D1Settings",
    "settings_manager",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        # ._async
        "D1Client": "._async.client",
        "create_d1_client": "._async.registry",
        # .settings
        "D1Settings": ".settings",
        "settings_manager": ".settings",
    }

    parent = __name__.rsplit(".", 1)[0]
    globals()[name] = getattr(import_module(module_map[name], parent), name)
    return globals()[name]
