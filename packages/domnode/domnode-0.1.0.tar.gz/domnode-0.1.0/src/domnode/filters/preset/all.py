"""Preset: All filters (visibility + semantic)."""

from typing import Optional
from ...node import Node
from .visible import filter_visible
from .semantic import filter_semantic


def filter_all(node: Node) -> Optional[Node]:
    """
    Apply all filters (visibility + semantic).

    This is the most comprehensive filtering, combining:
    - All visibility filters
    - All semantic filters

    Args:
        node: Node to filter

    Returns:
        Fully filtered Node, or None if all removed

    Example:
        >>> from domnode.parsers import parse_html
        >>> from domnode.filters.preset import filter_all
        >>> html = '<div class="wrapper"><script>x</script><button role="button">OK</button></div>'
        >>> root = parse_html(html)
        >>> filtered = filter_all(root)
        >>> filtered.tag
        'button'
        >>> filtered.attrib
        {'role': 'button'}
    """
    result = filter_visible(node)
    if result is not None:
        result = filter_semantic(result)
    return result
