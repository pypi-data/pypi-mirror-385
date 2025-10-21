"""
.. include:: ../README.md
"""
import importlib_metadata


def _get_version(package):
    try:
        return importlib_metadata.version(package)
    except importlib_metadata.PackageNotFoundError:
        return "<not found>"


__version__ = _get_version(__package__)

from .utils.module import Module
