"""domnode - DOM nodes with browser rendering data for web automation."""

from .node import Node, Text, BoundingBox
from .parsers import parse_html, parse_cdp
from .filters import filter_visible, filter_semantic, filter_all

__version__ = "0.1.0"

__all__ = [
    # Types
    'Node',
    'Text',
    'BoundingBox',

    # Parsers
    'parse_html',
    'parse_cdp',

    # Filters (presets)
    'filter_visible',
    'filter_semantic',
    'filter_all',
]
