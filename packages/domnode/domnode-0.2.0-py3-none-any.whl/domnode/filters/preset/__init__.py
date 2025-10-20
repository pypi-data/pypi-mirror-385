"""Preset filter combinations."""

from .visible import filter_visible
from .semantic import filter_semantic
from .all import filter_all

__all__ = [
    'filter_visible',
    'filter_semantic',
    'filter_all',
]
