"""Preset: All visibility filters."""

from typing import Optional
from ...node import Node
from ..visibility import filter_non_visible_tags, filter_css_hidden, filter_zero_dimensions


def filter_visible(node: Node) -> Optional[Node]:
    """
    Apply all visibility filters.

    Removes:
    - Non-visible tags (script, style, head, meta, etc.)
    - CSS-hidden elements (display:none, visibility:hidden, opacity:0)
    - Zero-dimension elements (except positioned popups)

    Args:
        node: Node to filter

    Returns:
        Filtered Node with only visible elements, or None if all removed

    Example:
        >>> from domnode.parsers import parse_html
        >>> from domnode.filters.preset import filter_visible
        >>> html = '<div><script>x</script><button>Click</button></div>'
        >>> root = parse_html(html)
        >>> filtered = filter_visible(root)
        >>> len(filtered.children)  # Only button remains
        1
    """
    result = filter_non_visible_tags(node)
    if result is not None:
        result = filter_css_hidden(result)
    if result is not None:
        result = filter_zero_dimensions(result)
    return result
