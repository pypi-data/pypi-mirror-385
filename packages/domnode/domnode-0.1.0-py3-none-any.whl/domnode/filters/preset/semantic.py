"""Preset: All semantic filters."""

from typing import Optional
from ...node import Node
from ..semantic import filter_attributes, filter_empty, collapse_wrappers


def filter_semantic(node: Node) -> Optional[Node]:
    """
    Apply all semantic filters.

    - Keeps only semantic attributes (role, aria-*, type, name, etc.)
    - Removes empty nodes (no attributes, no children)
    - Collapses wrapper elements (single-child wrappers)

    Args:
        node: Node to filter

    Returns:
        Filtered Node with clean semantic structure, or None if all removed

    Example:
        >>> node = Node(tag='div', attrib={'class': 'wrapper', 'role': 'button'})
        >>> child = Node(tag='span', attrib={'id': 'x'})
        >>> node.append(child)
        >>> filtered = filter_semantic(node)
        >>> filtered.attrib
        {'role': 'button'}
    """
    result = filter_attributes(node)
    result = filter_empty(result) if result is not None else None
    result = collapse_wrappers(result) if result is not None else None
    return result
