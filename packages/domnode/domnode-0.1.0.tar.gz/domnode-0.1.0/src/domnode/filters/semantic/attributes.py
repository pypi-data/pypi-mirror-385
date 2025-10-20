"""Filter attributes to keep only semantic ones."""

from typing import Set
from ...node import Node, Text

# Semantic attributes to preserve
SEMANTIC_ATTRIBUTES: Set[str] = {
    "role",
    "aria-label",
    "aria-labelledby",
    "aria-describedby",
    "aria-checked",
    "aria-selected",
    "aria-expanded",
    "aria-hidden",
    "aria-disabled",
    "type",
    "name",
    "placeholder",
    "value",
    "alt",
    "title",
    "href",
    "disabled",
    "checked",
    "selected",
}


def filter_attributes(node: Node, keep: Set[str] = None) -> Node:
    """
    Keep only semantic attributes, remove all others.

    Args:
        node: Node to filter
        keep: Set of attributes to keep (defaults to SEMANTIC_ATTRIBUTES)

    Returns:
        New Node with only semantic attributes

    Example:
        >>> node = Node(tag='div', attrib={'class': 'foo', 'role': 'button'})
        >>> filtered = filter_attributes(node)
        >>> filtered.attrib
        {'role': 'button'}
    """
    if keep is None:
        keep = SEMANTIC_ATTRIBUTES

    # Filter attributes
    filtered_attrib = {k: v for k, v in node.attrib.items() if k in keep}

    # Create new node
    new_node = Node(
        tag=node.tag,
        attrib=filtered_attrib,
        styles=node.styles.copy(),
        bounds=node.bounds,
        metadata=node.metadata.copy(),
    )

    # Recursively filter children
    for child in node.children:
        if isinstance(child, Text):
            new_node.append(Text(child.content))
        elif isinstance(child, Node):
            filtered_child = filter_attributes(child, keep)
            new_node.append(filtered_child)

    return new_node
