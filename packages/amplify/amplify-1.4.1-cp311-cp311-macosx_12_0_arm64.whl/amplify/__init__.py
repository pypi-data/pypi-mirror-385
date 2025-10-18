from __future__ import annotations

import contextlib
import importlib.util
import sys
from types import ModuleType


# Promote C++ submodule to the top-level and replace this namespace by the module
def _assign_module(module_name: str, location: str = "") -> ModuleType:
    def load_module(name: str) -> ModuleType:
        from importlib.abc import Loader  # noqa: PLC0415
        from importlib.machinery import ModuleSpec  # noqa: PLC0415
        from typing import TypeVar  # noqa: PLC0415

        T = TypeVar("T", ModuleSpec, ModuleType, Loader)

        def raise_if_none(obj: T | None) -> T:
            if obj is None:
                msg = f"No module named {name}"
                raise ModuleNotFoundError(msg)
            return obj

        spec = raise_if_none(importlib.util.find_spec(name))
        if not location:
            spec = raise_if_none(importlib.util.spec_from_file_location(spec.name.split(".")[-1], spec.origin))
        module = raise_if_none(importlib.util.module_from_spec(spec))
        raise_if_none(spec.loader).exec_module(module)
        return module

    module = load_module(module_name)

    # act as if loaded module were a package
    if not hasattr(module, "__path__") or not module.__path__:
        module.__path__ = __path__  # type: ignore  # noqa: F405

    if location:
        vars(sys.modules[__name__]).update({location: module})
        location = f"{__name__}.{location}"
    else:
        location = __name__

    sys.modules[location] = module

    return module


module = _assign_module(f"{__name__}.{__name__}")
with contextlib.suppress(ModuleNotFoundError):
    _assign_module("amplify_qaoa", "qaoa")

del _assign_module

# imports backward compatibility module
from ._backward import *  # noqa: E402, F403

# merge local variables into the module
vars(module).update({k: v for k, v in locals().items() if not k.startswith("_") and k != "annotations"})
