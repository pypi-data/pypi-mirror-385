"""Top-level package for imsi."""

__author__ = "CCCma Technical Development Team"
__email__ = ""

from importlib.metadata import version as get_version, PackageNotFoundError

try:
    # Use installed package version (when installed via pip)
    __version__ = get_version("cimsi")
except PackageNotFoundError:
    try:
        # Use locally generated setuptools_scm file (for local dev)
        from ._version import version as __version__
    except ImportError:
        __version__ = "unknown"
