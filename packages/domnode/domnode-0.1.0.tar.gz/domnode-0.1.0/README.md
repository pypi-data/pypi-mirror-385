# domnode

**DOM nodes with browser rendering data for web automation.**

`domnode` is a Python library that provides DOM node types enriched with browser rendering information (computed styles, bounding boxes, CDP metadata). It includes parsers for HTML and Chrome DevTools Protocol (CDP) snapshots, plus powerful filtering utilities to extract only visible, semantic content.

## Features

- 🌳 **Rich DOM nodes**: Includes computed styles, bounding boxes, and CDP backend node IDs
- 📦 **Dual parsers**: Parse from HTML strings or CDP snapshots
- 🎯 **Smart filtering**: Remove hidden elements, non-semantic attributes, and wrapper divs
- 🔍 **Visibility detection**: Handle `display:none`, `visibility:hidden`, `opacity:0`, zero-size elements
- 🏷️ **Semantic extraction**: Keep only meaningful attributes (role, aria-*, type, href, etc.)
- 🧹 **Tree optimization**: Collapse unnecessary wrapper elements
- ✅ **Well-tested**: 86 unit tests with comprehensive coverage

## Installation

```bash
pip install domnode
```

## Quick Start

```python
from domnode import parse_html, filter_visible

# Parse HTML
html = """
<div>
    <script>console.log('hidden')</script>
    <div style="display: none">Hidden content</div>
    <button role="button" class="btn">Click me</button>
</div>
"""

root = parse_html(html)

# Filter to only visible elements
visible = filter_visible(root)

# Result: Only the button remains
for child in visible:
    print(child.tag, child.attrib)
# Output: button {'role': 'button', 'class': 'btn'}
```

## Usage

### Parsing HTML

```python
from domnode.parsers import parse_html

html = '<div class="container"><button>Click</button></div>'
root = parse_html(html)

print(root.tag)          # 'div'
print(root.attrib)       # {'class': 'container'}
print(root.children[0])  # Node(tag='button', ...)
```

### Parsing CDP Snapshots

```python
from domnode.parsers import parse_cdp

# From Playwright/Puppeteer
snapshot = await page.cdp_session.send('DOMSnapshot.captureSnapshot', {
    'computedStyles': [],
    'includeDOMRects': True
})

root = parse_cdp(snapshot)
print(root.bounds)  # BoundingBox(x=0, y=0, width=1920, height=1080)
print(root.styles)  # {'display': 'block', 'position': 'static', ...}
```

### Filtering - Visibility

Remove hidden and non-visible elements:

```python
from domnode import parse_html, filter_visible

html = """
<div>
    <script>alert('hidden')</script>
    <style>.hide { display: none; }</style>
    <div style="display: none">Hidden</div>
    <div style="opacity: 0">Invisible</div>
    <button>Visible</button>
</div>
"""

root = parse_html(html)
visible = filter_visible(root)

# Only button remains
assert len(visible.children) == 1
assert visible.children[0].tag == 'button'
```

### Filtering - Semantic

Keep only semantic attributes and clean structure:

```python
from domnode import parse_html, filter_semantic

html = """
<div class="wrapper" id="container">
    <div class="inner">
        <button class="btn" role="button" aria-label="Submit">Click</button>
    </div>
</div>
"""

root = parse_html(html)
semantic = filter_semantic(root)

# Wrappers collapsed, only semantic attributes remain
assert semantic.tag == 'button'
assert semantic.attrib == {'role': 'button', 'aria-label': 'Submit'}
```

### Filtering - All (Visibility + Semantic)

```python
from domnode import parse_html, filter_all

html = """
<html>
    <head>
        <script src="app.js"></script>
    </head>
    <body class="page">
        <div class="wrapper">
            <button class="btn" role="button">Click</button>
        </div>
    </body>
</html>
"""

root = parse_html(html)
clean = filter_all(root)

# Head removed, wrappers collapsed, only semantic attributes
assert clean.tag == 'button'
assert clean.attrib == {'role': 'button'}
```

### Granular Filtering

Use individual filters for fine-grained control:

```python
from domnode.parsers import parse_html
from domnode.filters.visibility import filter_css_hidden, filter_zero_dimensions
from domnode.filters.semantic import filter_attributes, collapse_wrappers

root = parse_html(html)

# Apply specific filters
root = filter_css_hidden(root)
root = filter_attributes(root)
root = collapse_wrappers(root)
```

### Working with Nodes

```python
from domnode import Node, Text, BoundingBox

# Create nodes
div = Node(tag='div', attrib={'class': 'container'})
button = Node(
    tag='button',
    attrib={'role': 'button'},
    styles={'display': 'block'},
    bounds=BoundingBox(x=10, y=20, width=100, height=50)
)

# Build tree
div.append(Text('Click here: '))
div.append(button)
button.append(Text('Submit'))

# Navigate
for child in div:
    if isinstance(child, Node):
        print(f"Element: {child.tag}")
    elif isinstance(child, Text):
        print(f"Text: {child.content}")

# Get all text
print(div.get_text())  # "Click here: Submit"

# Check visibility
print(button.is_visible())      # True
print(button.has_zero_size())   # False
```

## API Reference

### Types

- **`Node`**: DOM element with tag, attributes, styles, bounds, metadata, and children
- **`Text`**: Text node with content
- **`BoundingBox`**: Element bounding box (x, y, width, height)

### Parsers

- **`parse_html(html: str) -> Node`**: Parse HTML string to Node tree
- **`parse_cdp(snapshot: dict) -> Node`**: Parse CDP snapshot to Node tree

### Filters

#### Presets (convenience)
- **`filter_visible(node) -> Node | None`**: Remove all hidden elements
- **`filter_semantic(node) -> Node | None`**: Keep only semantic content
- **`filter_all(node) -> Node | None`**: Apply all filters

#### Visibility Filters
- **`filter_non_visible_tags(node)`**: Remove script, style, head, meta, etc.
- **`filter_css_hidden(node)`**: Remove display:none, visibility:hidden, opacity:0
- **`filter_zero_dimensions(node)`**: Remove zero-width/height elements

#### Semantic Filters
- **`filter_attributes(node, keep=SEMANTIC_ATTRIBUTES)`**: Keep only semantic attributes
- **`filter_empty(node)`**: Remove empty nodes (no attributes, no children)
- **`collapse_wrappers(node)`**: Collapse single-child wrapper elements

### Node Methods

- **`node.append(child)`**: Add a child node or text
- **`node.remove(child)`**: Remove a child
- **`node.is_visible()`**: Check if element is visible (based on styles)
- **`node.has_zero_size()`**: Check if element has zero dimensions
- **`node.get_text(separator='')`**: Get all text content recursively

## Architecture

`domnode` is designed as a foundational library for web automation:

```
┌─────────────────────┐
│   natural-selector  │  (RAG-based element selection)
│   (embeddings, LLM) │
└──────────┬──────────┘
           │ uses
┌──────────▼──────────┐
│     domcontext      │  (LLM context formatting)
│  (markdown, tokens) │
└──────────┬──────────┘
           │ uses
┌──────────▼──────────┐
│      domnode        │  (Core DOM + filtering)
│  (this package)     │
└─────────────────────┘
```

## Semantic Attributes

By default, `filter_attributes` keeps these semantic attributes:

```python
SEMANTIC_ATTRIBUTES = {
    "role", "aria-label", "aria-labelledby", "aria-describedby",
    "aria-checked", "aria-selected", "aria-expanded", "aria-hidden",
    "aria-disabled", "type", "name", "placeholder", "value",
    "alt", "title", "href", "disabled", "checked", "selected"
}
```

You can customize:
```python
from domnode.filters.semantic import filter_attributes

custom_attrs = {"role", "href", "data-test-id"}
filtered = filter_attributes(node, keep=custom_attrs)
```

## Use Cases

### Web Scraping
Extract only visible, meaningful content from web pages.

### Browser Automation
Filter DOM to only interactive elements for AI agents.

### LLM Context
Reduce HTML to essential semantic structure for language models.

### Accessibility Testing
Analyze semantic attributes and ARIA labels.

### Testing
Build and manipulate DOM trees programmatically.

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/domnode.git
cd domnode

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=domnode --cov-report=html
```

## Testing

The package includes 86 comprehensive unit tests covering:
- Core node types and operations
- HTML and CDP parsing
- All visibility filters
- All semantic filters
- Preset filter combinations
- Edge cases and error handling

```bash
pytest -v
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- **[domcontext](https://github.com/yourusername/domcontext)**: DOM to LLM context with markdown serialization
- **[natural-selector](https://github.com/yourusername/natural-selector)**: Natural language element selection with RAG

## Changelog

### 0.1.0 (2025-01-XX)
- Initial release
- Core Node, Text, BoundingBox types
- HTML and CDP parsers
- Visibility and semantic filters
- 86 unit tests
