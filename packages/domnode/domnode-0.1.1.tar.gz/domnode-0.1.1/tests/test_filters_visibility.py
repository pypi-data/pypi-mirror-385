"""Tests for visibility filters."""

import pytest
from domnode.node import Node, Text, BoundingBox
from domnode.filters.visibility import (
    filter_non_visible_tags,
    filter_css_hidden,
    filter_zero_dimensions,
)


class TestFilterNonVisibleTags:
    """Tests for filter_non_visible_tags."""

    def test_remove_script_tag(self):
        root = Node(tag="div")
        root.append(Node(tag="script"))
        root.append(Node(tag="button"))

        filtered = filter_non_visible_tags(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_remove_style_tag(self):
        root = Node(tag="div")
        root.append(Node(tag="style"))
        root.append(Node(tag="p"))

        filtered = filter_non_visible_tags(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "p"

    def test_remove_head_tag(self):
        root = Node(tag="html")
        root.append(Node(tag="head"))
        root.append(Node(tag="body"))

        filtered = filter_non_visible_tags(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "body"

    def test_remove_multiple_non_visible_tags(self):
        root = Node(tag="div")
        root.append(Node(tag="script"))
        root.append(Node(tag="style"))
        root.append(Node(tag="meta"))
        root.append(Node(tag="button"))

        filtered = filter_non_visible_tags(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_keep_text_nodes(self):
        root = Node(tag="div")
        root.append(Text("Hello"))
        root.append(Node(tag="script"))

        filtered = filter_non_visible_tags(root)
        assert len(filtered.children) == 1
        assert isinstance(filtered.children[0], Text)
        assert filtered.children[0].content == "Hello"

    def test_return_none_if_root_is_non_visible(self):
        script = Node(tag="script")
        filtered = filter_non_visible_tags(script)
        assert filtered is None

    def test_nested_non_visible_tags(self):
        root = Node(tag="div")
        child = Node(tag="span")
        child.append(Node(tag="script"))
        child.append(Node(tag="button"))
        root.append(child)

        filtered = filter_non_visible_tags(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "span"
        assert len(filtered.children[0].children) == 1
        assert filtered.children[0].children[0].tag == "button"


class TestFilterCSSHidden:
    """Tests for filter_css_hidden."""

    def test_remove_display_none(self):
        root = Node(tag="div")
        root.append(Node(tag="div", styles={"display": "none"}))
        root.append(Node(tag="button"))

        filtered = filter_css_hidden(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_remove_visibility_hidden(self):
        root = Node(tag="div")
        root.append(Node(tag="div", styles={"visibility": "hidden"}))
        root.append(Node(tag="button"))

        filtered = filter_css_hidden(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_remove_opacity_zero(self):
        root = Node(tag="div")
        root.append(Node(tag="div", styles={"opacity": "0"}))
        root.append(Node(tag="button"))

        filtered = filter_css_hidden(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_keep_opacity_non_zero(self):
        root = Node(tag="div")
        root.append(Node(tag="div", styles={"opacity": "0.5"}))

        filtered = filter_css_hidden(root)
        assert len(filtered.children) == 1

    def test_remove_hidden_attribute(self):
        root = Node(tag="div")
        root.append(Node(tag="div", attrib={"hidden": ""}))
        root.append(Node(tag="button"))

        filtered = filter_css_hidden(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_remove_hidden_input(self):
        root = Node(tag="form")
        root.append(Node(tag="input", attrib={"type": "hidden"}))
        root.append(Node(tag="input", attrib={"type": "text"}))

        filtered = filter_css_hidden(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].attrib["type"] == "text"

    def test_keep_text_nodes(self):
        root = Node(tag="div")
        root.append(Text("Hello"))

        filtered = filter_css_hidden(root)
        assert len(filtered.children) == 1
        assert isinstance(filtered.children[0], Text)

    def test_return_none_if_root_is_hidden(self):
        div = Node(tag="div", styles={"display": "none"})
        filtered = filter_css_hidden(div)
        assert filtered is None

    def test_nested_hidden_elements(self):
        root = Node(tag="div")
        child = Node(tag="span")
        child.append(Node(tag="div", styles={"display": "none"}))
        child.append(Node(tag="button"))
        root.append(child)

        filtered = filter_css_hidden(root)
        assert len(filtered.children[0].children) == 1
        assert filtered.children[0].children[0].tag == "button"


class TestFilterZeroDimensions:
    """Tests for filter_zero_dimensions."""

    def test_remove_zero_width(self):
        root = Node(tag="div")
        root.append(Node(tag="div", bounds=BoundingBox(0, 0, 0, 50)))
        root.append(Node(tag="button", bounds=BoundingBox(0, 0, 100, 50)))

        filtered = filter_zero_dimensions(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_remove_zero_height(self):
        root = Node(tag="div")
        root.append(Node(tag="div", bounds=BoundingBox(0, 0, 100, 0)))
        root.append(Node(tag="button", bounds=BoundingBox(0, 0, 100, 50)))

        filtered = filter_zero_dimensions(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_keep_element_without_bounds(self):
        root = Node(tag="div")
        root.append(Node(tag="button"))

        filtered = filter_zero_dimensions(root)
        assert len(filtered.children) == 1

    def test_keep_zero_size_with_visible_children(self):
        # Positioned popup scenario
        root = Node(tag="div")
        popup = Node(tag="div", bounds=BoundingBox(0, 0, 0, 0))
        popup.append(Node(tag="button", bounds=BoundingBox(100, 100, 80, 40)))
        root.append(popup)

        filtered = filter_zero_dimensions(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "div"
        assert len(filtered.children[0].children) == 1

    def test_remove_zero_size_without_visible_children(self):
        root = Node(tag="div")
        empty = Node(tag="div", bounds=BoundingBox(0, 0, 0, 0))
        root.append(empty)

        filtered = filter_zero_dimensions(root)
        assert len(filtered.children) == 0

    def test_keep_text_nodes(self):
        root = Node(tag="div")
        root.append(Text("Hello"))

        filtered = filter_zero_dimensions(root)
        assert len(filtered.children) == 1
        assert isinstance(filtered.children[0], Text)

    def test_return_none_if_root_is_zero_size_no_children(self):
        div = Node(tag="div", bounds=BoundingBox(0, 0, 0, 0))
        filtered = filter_zero_dimensions(div)
        assert filtered is None

    def test_nested_zero_dimensions(self):
        root = Node(tag="div")
        child = Node(tag="span")
        child.append(Node(tag="div", bounds=BoundingBox(0, 0, 0, 50)))
        child.append(Node(tag="button", bounds=BoundingBox(0, 0, 100, 50)))
        root.append(child)

        filtered = filter_zero_dimensions(root)
        assert len(filtered.children[0].children) == 1
        assert filtered.children[0].children[0].tag == "button"
