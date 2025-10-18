from . import pyAtmoWeb as _pyatmoweb
from .pyAtmoWeb import *

__all__ = getattr(_pyatmoweb, "__all__", [name for name in globals() if not name.startswith("_")])
__version__ = "0.0.3"