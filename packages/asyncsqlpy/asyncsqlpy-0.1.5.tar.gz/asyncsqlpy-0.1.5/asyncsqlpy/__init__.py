"""
asyncsqlpy
-----------

Async SQL + Redis wrapper with Mongo-like interface.
Supports both compiled (.so) and pure Python versions.
"""

# Try to import compiled core (for Nuitka build)
try:
    from .asyncsqlpy import *  # for pure Python module
except ImportError:
    pass

try:
    from .asyncsqlpy import *  # compiled module (asyncsqlpy.so)
except Exception:
    pass

__version__ = "0.1.3"
__all__ = globals().get("__all__", [])
