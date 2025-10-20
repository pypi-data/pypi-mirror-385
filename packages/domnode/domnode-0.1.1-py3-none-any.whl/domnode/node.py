"""Core DOM node types with browser rendering data."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any


@dataclass
class BoundingBox:
    """Element bounding box from browser rendering."""
    x: float
    y: float
    width: float
    height: float


@dataclass
class Node:
    """
    DOM element node with browser rendering data.

    Attributes:
        tag: Element tag name (e.g., 'div', 'button')
        attrib: Element attributes as key-value pairs
        styles: Computed CSS styles from browser
        bounds: Element bounding box (position and dimensions)
        metadata: Parser-specific metadata (e.g., backend_node_id, source_line)
        children: Child nodes (can be Node or Text)
        parent: Parent node reference
    """

    tag: str
    attrib: Dict[str, str] = field(default_factory=dict)

    # Browser rendering data
    styles: Dict[str, str] = field(default_factory=dict)
    bounds: Optional[BoundingBox] = None

    # Generic metadata for parser-specific data
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Tree structure
    children: List[Union['Node', 'Text']] = field(default_factory=list)
    parent: Optional['Node'] = field(default=None, repr=False)

    def __iter__(self):
        """Iterate over children."""
        return iter(self.children)

    def __len__(self):
        """Number of children."""
        return len(self.children)

    def __getitem__(self, index: int):
        """Get child by index."""
        return self.children[index]

    def append(self, child: Union['Node', 'Text']):
        """Add a child node."""
        self.children.append(child)
        child.parent = self

    def remove(self, child: Union['Node', 'Text']):
        """Remove a child node."""
        self.children.remove(child)
        child.parent = None

    def is_visible(self) -> bool:
        """
        Check if element is visible based on computed styles.

        Returns False if:
        - display: none
        - visibility: hidden
        - opacity: 0
        """
        if self.styles.get('display') == 'none':
            return False
        if self.styles.get('visibility') == 'hidden':
            return False
        try:
            if float(self.styles.get('opacity', '1')) == 0:
                return False
        except (ValueError, TypeError):
            pass
        return True

    def has_zero_size(self) -> bool:
        """Check if element has zero width or height."""
        if not self.bounds:
            return False
        return self.bounds.width == 0 or self.bounds.height == 0

    def get_text(self, separator: str = '') -> str:
        """
        Get all text content from this node and descendants.

        Args:
            separator: String to join text parts with

        Returns:
            Combined text content
        """
        parts = []
        for child in self.children:
            if isinstance(child, Text):
                parts.append(child.content)
            elif isinstance(child, Node):
                parts.append(child.get_text(separator))
        return separator.join(parts)


@dataclass
class Text:
    """
    DOM text node.

    Attributes:
        content: Text content
        parent: Parent node reference
    """
    content: str
    parent: Optional[Node] = field(default=None, repr=False)

    def __str__(self):
        return self.content
