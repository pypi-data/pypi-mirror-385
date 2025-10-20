"""Tests for parsers."""

import pytest
from domnode.parsers import parse_html, parse_cdp
from domnode.node import Node, Text


class TestParseHTML:
    """Tests for parse_html."""

    def test_parse_simple_html(self):
        html = "<div>Hello</div>"
        root = parse_html(html)

        assert root.tag == "div"
        assert len(root.children) == 1
        assert isinstance(root.children[0], Text)
        assert root.children[0].content == "Hello"

    def test_parse_nested_html(self):
        html = "<div><span>Hello</span></div>"
        root = parse_html(html)

        assert root.tag == "div"
        assert len(root.children) == 1
        assert isinstance(root.children[0], Node)
        assert root.children[0].tag == "span"
        assert root.children[0].children[0].content == "Hello"

    def test_parse_with_attributes(self):
        html = '<button class="btn" role="button">Click</button>'
        root = parse_html(html)

        assert root.tag == "button"
        assert root.attrib["class"] == "btn"
        assert root.attrib["role"] == "button"

    def test_parse_with_text_and_elements(self):
        html = "<div>Hello <span>world</span>!</div>"
        root = parse_html(html)

        assert root.tag == "div"
        assert len(root.children) == 3
        assert root.children[0].content == "Hello"
        assert root.children[1].tag == "span"
        assert root.children[2].content == "!"

    def test_parse_with_backend_node_id(self):
        html = '<div backend_node_id="123">Content</div>'
        root = parse_html(html)

        assert root.tag == "div"
        assert root.metadata["backend_node_id"] == 123
        # backend_node_id should not be in attrib
        assert "backend_node_id" not in root.attrib

    def test_parse_with_bounding_box(self):
        html = '<div bounding_box_rect="10,20,100,50">Content</div>'
        root = parse_html(html)

        assert root.bounds is not None
        assert root.bounds.x == 10
        assert root.bounds.y == 20
        assert root.bounds.width == 100
        assert root.bounds.height == 50
        # bounding_box_rect should not be in attrib
        assert "bounding_box_rect" not in root.attrib

    def test_parse_with_inline_styles(self):
        html = '<div style="display: block; color: red">Content</div>'
        root = parse_html(html)

        assert root.styles["display"] == "block"
        assert root.styles["color"] == "red"

    def test_parse_empty_html(self):
        root = parse_html("")
        assert root.tag == "html"

    def test_parse_whitespace_html(self):
        root = parse_html("   ")
        assert root.tag == "html"

    def test_parse_multiple_children(self):
        html = "<div><p>A</p><p>B</p><p>C</p></div>"
        root = parse_html(html)

        assert len(root.children) == 3
        assert all(isinstance(c, Node) and c.tag == "p" for c in root.children)

    def test_parse_special_text_tag(self):
        # Mind2Web dataset uses <text> tags
        html = '<div><text>Content</text></div>'
        root = parse_html(html)

        # <text> should be converted to span with text content
        assert root.tag == "div"
        assert len(root.children) == 1
        assert root.children[0].tag == "span"


class TestParseCDP:
    """Tests for parse_cdp."""

    def test_parse_simple_cdp(self):
        snapshot = {
            "documents": [
                {
                    "nodes": {
                        "nodeType": [1, 3],  # Element, Text
                        "nodeName": [0, 1],  # Indices into strings
                        "nodeValue": [-1, 2],
                        "parentIndex": [-1, 0],
                        "attributes": [[], []],
                    }
                }
            ],
            "strings": ["div", "#text", "Hello"],
        }

        root = parse_cdp(snapshot)
        assert root.tag == "div"
        assert len(root.children) == 1
        assert isinstance(root.children[0], Text)
        assert root.children[0].content == "Hello"

    def test_parse_cdp_with_attributes(self):
        snapshot = {
            "documents": [
                {
                    "nodes": {
                        "nodeType": [1],  # Element
                        "nodeName": [0],  # "button"
                        "nodeValue": [-1],
                        "parentIndex": [-1],
                        "attributes": [[1, 2, 3, 4]],  # class="btn", role="button"
                    }
                }
            ],
            "strings": ["button", "class", "btn", "role", "button"],
        }

        root = parse_cdp(snapshot)
        assert root.tag == "button"
        assert root.attrib["class"] == "btn"
        assert root.attrib["role"] == "button"

    def test_parse_cdp_with_layout(self):
        snapshot = {
            "documents": [
                {
                    "nodes": {
                        "nodeType": [1],
                        "nodeName": [0],
                        "nodeValue": [-1],
                        "parentIndex": [-1],
                        "attributes": [[]],
                    },
                    "layout": {
                        "nodeIndex": [0],
                        "bounds": [[10, 20, 100, 50]],
                        "styles": [[1, 2, 3, 4]],  # display: block
                    },
                }
            ],
            "strings": ["div", "display", "block", "color", "red"],
        }

        root = parse_cdp(snapshot)
        assert root.bounds.x == 10
        assert root.bounds.y == 20
        assert root.bounds.width == 100
        assert root.bounds.height == 50
        assert root.styles["display"] == "block"
        assert root.styles["color"] == "red"

    def test_parse_cdp_nested_elements(self):
        snapshot = {
            "documents": [
                {
                    "nodes": {
                        "nodeType": [1, 1, 3],  # div, span, text
                        "nodeName": [0, 1, 2],
                        "nodeValue": [-1, -1, 3],
                        "parentIndex": [-1, 0, 1],
                        "attributes": [[], [], []],
                    }
                }
            ],
            "strings": ["div", "span", "#text", "Hello"],
        }

        root = parse_cdp(snapshot)
        assert root.tag == "div"
        assert len(root.children) == 1
        assert root.children[0].tag == "span"
        assert root.children[0].children[0].content == "Hello"

    def test_parse_empty_cdp(self):
        snapshot = {"documents": [], "strings": []}
        root = parse_cdp(snapshot)
        assert root.tag == "html"

    def test_parse_cdp_with_metadata(self):
        snapshot = {
            "documents": [
                {
                    "nodes": {
                        "nodeType": [1],
                        "nodeName": [0],
                        "nodeValue": [-1],
                        "parentIndex": [-1],
                        "attributes": [[]],
                    }
                }
            ],
            "strings": ["div"],
        }

        root = parse_cdp(snapshot)
        assert root.metadata["backend_node_id"] == 0
        assert root.metadata["cdp_index"] == 0
