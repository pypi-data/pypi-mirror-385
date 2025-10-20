"""Remove non-visible tags (script, style, head, etc.)."""

from typing import Optional
from ...node import Node, Text

# Non-visible tags that should be removed
NON_VISIBLE_TAGS = {
    "script",
    "style",
    "head",
    "meta",
    "link",
    "title",
    "noscript",
}


def filter_non_visible_tags(node: Node) -> Optional[Node]:
    """
    Remove non-visible tags (script, style, head, meta, etc.).

    Args:
        node: Node to filter

    Returns:
        New Node without non-visible tags, or None if node itself is non-visible

    Example:
        >>> root = Node(tag='div')
        >>> root.append(Node(tag='script'))
        >>> root.append(Node(tag='button'))
        >>> filtered = filter_non_visible_tags(root)
        >>> len(filtered.children)  # Only button remains
        1
    """
    # Check if this node should be removed
    if node.tag in NON_VISIBLE_TAGS:
        return None

    # Create new node with same properties
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
            # Keep text nodes
            new_node.append(Text(child.content))
        elif isinstance(child, Node):
            filtered_child = filter_non_visible_tags(child)
            if filtered_child is not None:
                new_node.append(filtered_child)

    return new_node
