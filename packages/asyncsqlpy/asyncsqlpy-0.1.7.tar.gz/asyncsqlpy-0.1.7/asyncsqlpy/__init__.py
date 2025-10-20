try:
    from .core import *   # compiled Nuitka module
except ImportError:
    from .core import *  # fallback to pure Python version

__version__ = "0.1.7"
