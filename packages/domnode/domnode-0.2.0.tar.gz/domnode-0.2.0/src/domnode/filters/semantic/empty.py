"""Remove empty nodes."""

from typing import Optional
from ...node import Node, Text

# Interactive tags to keep even if empty
INTERACTIVE_TAGS = {"a", "button", "input", "select", "textarea", "label"}


def filter_empty(node: Node) -> Optional[Node]:
    """
    Remove empty nodes (no attributes and no children).

    Exception: Keeps interactive elements even if empty (button, input, etc.)

    Args:
        node: Node to filter

    Returns:
        New Node without empty nodes, or None if node itself is empty

    Example:
        >>> div = Node(tag='div')  # No attributes, no children
        >>> filtered = filter_empty(div)
        >>> filtered is None
        True
    """
    # Recursively filter children first
    filtered_children = []
    for child in node.children:
        if isinstance(child, Text):
            # Keep text with content
            if child.content.strip():
                filtered_children.append(Text(child.content))
        elif isinstance(child, Node):
            filtered_child = filter_empty(child)
            if filtered_child is not None:
                filtered_children.append(filtered_child)

    # Check if node is empty
    has_attributes = bool(node.attrib)
    has_children = len(filtered_children) > 0
    is_interactive = node.tag in INTERACTIVE_TAGS

    # Remove if empty (no attributes, no children) and not interactive
    if not has_attributes and not has_children and not is_interactive:
        return None

    # Create new node
    new_node = Node(
        tag=node.tag,
        attrib=node.attrib.copy(),
        styles=node.styles.copy(),
        bounds=node.bounds,
        metadata=node.metadata.copy(),
    )

    # Add filtered children
    for child in filtered_children:
        new_node.append(child)

    return new_node
