"""Remove CSS-hidden elements (display:none, visibility:hidden, opacity:0)."""

from typing import Optional
from ...node import Node, Text


def filter_css_hidden(node: Node) -> Optional[Node]:
    """
    Remove CSS-hidden elements (display:none, visibility:hidden, opacity:0).

    Also removes:
    - Elements with hidden attribute
    - <input type="hidden">

    Args:
        node: Node to filter

    Returns:
        New Node without CSS-hidden elements, or None if node itself is hidden

    Example:
        >>> div = Node(tag='div', styles={'display': 'none'})
        >>> filtered = filter_css_hidden(div)
        >>> filtered is None
        True
    """
    # Check computed styles
    display = node.styles.get("display", "").lower()
    visibility = node.styles.get("visibility", "").lower()
    opacity = node.styles.get("opacity", "1")

    # Filter CSS-hidden elements
    if display == "none":
        return None
    if visibility == "hidden":
        return None
    try:
        if float(opacity) == 0:
            return None
    except (ValueError, TypeError):
        pass

    # Check hidden attribute
    if "hidden" in node.attrib:
        return None

    # Check for hidden input
    if node.tag == "input" and node.attrib.get("type", "").lower() == "hidden":
        return None

    # Create new node
    new_node = Node(
        tag=node.tag,
        attrib=node.attrib.copy(),
        styles=node.styles.copy(),
        bounds=node.bounds,
        metadata=node.metadata.copy(),
    )

    # Recursively filter children
    for child in node.children:
        if isinstance(child, Text):
            new_node.append(Text(child.content))
        elif isinstance(child, Node):
            filtered_child = filter_css_hidden(child)
            if filtered_child is not None:
                new_node.append(filtered_child)

    return new_node
