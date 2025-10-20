# domnode

DOM nodes with browser rendering data for web automation.

A Python library for parsing and filtering DOM trees with browser rendering information. Supports HTML and Chrome DevTools Protocol snapshots.

## Installation

```bash
pip install domnode
```

## Quick Start

```python
from domnode import parse_html, filter_visible

html = """
<div>
    <script>console.log('hidden')</script>
    <div style="display: none">Hidden content</div>
    <button role="button" class="btn">Click me</button>
</div>
"""

root = parse_html(html)
visible = filter_visible(root)

for child in visible:
    print(child.tag, child.attrib)
# Output: button {'role': 'button', 'class': 'btn'}
```

## Features

- Parse HTML strings and CDP snapshots into rich DOM trees
- Filter visibility (display:none, visibility:hidden, opacity:0, zero-size)
- Filter semantically (keep only meaningful attributes, collapse wrappers)
- Access computed styles and bounding boxes
- 86 comprehensive unit tests

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

### Filtering Visible Elements

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

### Filtering Semantic Content

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

### Combining Filters

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

**Node**
DOM element with tag, attributes, styles, bounds, metadata, and children.

**Text**
Text node with content.

**BoundingBox**
Element bounding box with x, y, width, height.

### Parsers

**parse_html(html: str) -> Node**
Parse HTML string to Node tree.

**parse_cdp(snapshot: dict) -> Node**
Parse CDP snapshot to Node tree.

### Preset Filters

**filter_visible(node) -> Node | None**
Remove all hidden elements.

**filter_semantic(node) -> Node | None**
Keep only semantic content.

**filter_all(node) -> Node | None**
Apply all filters.

### Visibility Filters

**filter_non_visible_tags(node)**
Remove script, style, head, meta, etc.

**filter_css_hidden(node)**
Remove display:none, visibility:hidden, opacity:0.

**filter_zero_dimensions(node)**
Remove zero-width/height elements.

### Semantic Filters

**filter_attributes(node, keep=SEMANTIC_ATTRIBUTES)**
Keep only semantic attributes.

**filter_empty(node)**
Remove empty nodes.

**collapse_wrappers(node)**
Collapse single-child wrapper elements.

### Node Methods

**node.append(child)**
Add a child node or text.

**node.remove(child)**
Remove a child.

**node.is_visible()**
Check if element is visible.

**node.has_zero_size()**
Check if element has zero dimensions.

**node.get_text(separator='')**
Get all text content recursively.

## Semantic Attributes

By default, filter_attributes keeps these attributes:

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

**Web Scraping**
Extract only visible, meaningful content from web pages.

**Browser Automation**
Filter DOM to only interactive elements for AI agents.

**LLM Context**
Reduce HTML to essential semantic structure for language models.

**Accessibility Testing**
Analyze semantic attributes and ARIA labels.

**Testing**
Build and manipulate DOM trees programmatically.

## Development

```bash
# Clone repository
git clone https://github.com/steve-z-wang/domnode.git
cd domnode

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=domnode --cov-report=html
```

## License

MIT

## Contributing

Contributions are welcome. Please submit a Pull Request.

## Related Projects

[domcontext](https://github.com/steve-z-wang/domcontext) - DOM to LLM context with markdown serialization

[natural-selector](https://github.com/steve-z-wang/natural-selector) - Natural language element selection with RAG
