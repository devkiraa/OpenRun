"""OpenRun core package."""

from .server import serve
import importlib.metadata

try:
    __version__ = importlib.metadata.version("openrun-llm")
except importlib.metadata.PackageNotFoundError:
    __version__ = "dev"

__all__ = ["serve"]
