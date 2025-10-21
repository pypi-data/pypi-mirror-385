from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("napistu-py")
except PackageNotFoundError:
    # package is not installed
    pass
