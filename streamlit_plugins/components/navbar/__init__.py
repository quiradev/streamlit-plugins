from importlib import import_module as _import_module
from typing import Any as _Any

from . import v1
from .v1 import *

st_navbar_v1 = v1.st_navbar


def st_navbar_v2(*args: _Any, **kwargs: _Any) -> str:
    return _import_module(f"{__name__}.v2").st_navbar(*args, **kwargs)
