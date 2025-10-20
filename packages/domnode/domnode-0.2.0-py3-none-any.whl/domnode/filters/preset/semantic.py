"""Preset: All semantic filters."""

from typing import Optional
from ...node import Node
from ..semantic import (
    filter_attributes,
    filter_empty,
    collapse_single_child_wrappers,
    filter_presentational_roles,
)


def filter_semantic(node: Node) -> Optional[Node]:
    """
    Apply all semantic filters.

    - Keeps only semantic attributes (role, aria-*, type, name, etc.)
    - Filters presentational roles (removes role='none' or role='presentation')
    - Removes empty nodes (no attributes, no children)
    - Collapses single-child wrapper elements

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
    result = filter_presentational_roles(result) if result is not None else None
    result = filter_empty(result) if result is not None else None
    result = collapse_single_child_wrappers(result) if result is not None else None
    return result
