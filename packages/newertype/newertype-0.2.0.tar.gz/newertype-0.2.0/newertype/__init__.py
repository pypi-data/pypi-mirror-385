from importlib.metadata import version

from .newertype import NewerType  # noqa: F401

_version = version("newertype")
__version__ = _version
