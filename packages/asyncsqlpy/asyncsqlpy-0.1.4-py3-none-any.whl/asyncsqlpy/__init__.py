# asyncsqlpy/__init__.py

from . import asyncsqlpy as _core
from .asyncsqlpy import *  # fallback if using pure Python build

__all__ = getattr(_core, "__all__", dir(_core))
