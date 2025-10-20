"""
Filters for DOM tree manipulation.

Import specific filters:
    from domnode.filters.visibility.css_hidden import filter_css_hidden
    from domnode.filters.semantic.attributes import filter_attributes
    from domnode.filters.preset.visible import filter_visible

Or use convenience imports:
    from domnode.filters import filter_visible  # Common presets
"""

# Re-export presets for convenience (most common usage)
from .preset import filter_visible, filter_semantic, filter_all

__all__ = [
    # Presets (commonly used)
    'filter_visible',
    'filter_semantic',
    'filter_all',
]
