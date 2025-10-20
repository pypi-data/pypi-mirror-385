"""Filter presentational role attributes (role='none' or role='presentation')."""

from ...node import Node, Text


def filter_presentational_roles(node: Node) -> Node:
    """
    Filter presentational role attributes.

    Removes role='none' or role='presentation' attributes from elements.
    These roles explicitly declare that an element has no semantic meaning,
    so we remove the confusing attribute while preserving the element structure.

    Args:
        node: Node to process

    Returns:
        New Node with presentational roles filtered out

    Example:
        >>> node = Node(tag='ul', attrib={'role': 'none'})
        >>> filtered = filter_presentational_roles(node)
        >>> filtered.attrib
        {}
    """
    # Check if this node has presentational role
    new_attrib = node.attrib.copy()
    role = new_attrib.get('role', '').lower()
    if role in ('none', 'presentation'):
        # Remove the role attribute
        del new_attrib['role']

    # Create new node
    new_node = Node(
        tag=node.tag,
        attrib=new_attrib,
        styles=node.styles.copy(),
        bounds=node.bounds,
        metadata=node.metadata.copy(),
    )

    # Recursively process children
    for child in node.children:
        if isinstance(child, Text):
            new_node.append(Text(child.content))
        elif isinstance(child, Node):
            filtered_child = filter_presentational_roles(child)
            new_node.append(filtered_child)

    return new_node
