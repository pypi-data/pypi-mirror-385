"""Semantic filters - clean attributes and structure."""

from .attributes import filter_attributes, SEMANTIC_ATTRIBUTES
from .empty import filter_empty, INTERACTIVE_TAGS
from .wrappers import collapse_wrappers

__all__ = [
    'filter_attributes',
    'filter_empty',
    'collapse_wrappers',
    'SEMANTIC_ATTRIBUTES',
    'INTERACTIVE_TAGS',
]
