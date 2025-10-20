import importlib.metadata

from .keys import KeyCode, KeyEventType
from .client import ManhattanRemote, ManhattanModel
from .exceptions import ManhattanError, ManhattanConnectionError, ManhattanTimeoutError


try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development mode

__all__ = [
    "KeyCode",
    "KeyEventType",
    "ManhattanRemote",
    "ManhattanModel",
    "ManhattanError",
    "ManhattanConnectionError",
    "ManhattanTimeoutError",
]