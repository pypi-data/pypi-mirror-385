"""Tests for core Node and Text types."""

import pytest
from domnode.node import Node, Text, BoundingBox


class TestBoundingBox:
    """Tests for BoundingBox."""

    def test_create_bounding_box(self):
        bbox = BoundingBox(x=10.5, y=20.0, width=100.0, height=50.0)
        assert bbox.x == 10.5
        assert bbox.y == 20.0
        assert bbox.width == 100.0
        assert bbox.height == 50.0


class TestNode:
    """Tests for Node."""

    def test_create_node(self):
        node = Node(tag="div")
        assert node.tag == "div"
        assert node.attrib == {}
        assert node.styles == {}
        assert node.bounds is None
        assert node.metadata == {}
        assert node.children == []
        assert node.parent is None

    def test_create_node_with_attributes(self):
        node = Node(
            tag="button",
            attrib={"class": "btn", "role": "button"},
            styles={"display": "block"},
            bounds=BoundingBox(0, 0, 100, 50),
            metadata={"backend_node_id": 123},
        )
        assert node.tag == "button"
        assert node.attrib == {"class": "btn", "role": "button"}
        assert node.styles == {"display": "block"}
        assert node.bounds.width == 100
        assert node.metadata["backend_node_id"] == 123

    def test_append_child(self):
        parent = Node(tag="div")
        child = Node(tag="span")
        parent.append(child)

        assert len(parent.children) == 1
        assert parent.children[0] is child
        assert child.parent is parent

    def test_append_text(self):
        parent = Node(tag="div")
        text = Text("Hello")
        parent.append(text)

        assert len(parent.children) == 1
        assert parent.children[0] is text
        assert text.parent is parent

    def test_remove_child(self):
        parent = Node(tag="div")
        child = Node(tag="span")
        parent.append(child)
        parent.remove(child)

        assert len(parent.children) == 0
        assert child.parent is None

    def test_iteration(self):
        parent = Node(tag="div")
        child1 = Node(tag="span")
        child2 = Text("Hello")
        parent.append(child1)
        parent.append(child2)

        children = list(parent)
        assert len(children) == 2
        assert children[0] is child1
        assert children[1] is child2

    def test_len(self):
        parent = Node(tag="div")
        assert len(parent) == 0

        parent.append(Node(tag="span"))
        assert len(parent) == 1

        parent.append(Text("Hello"))
        assert len(parent) == 2

    def test_getitem(self):
        parent = Node(tag="div")
        child = Node(tag="span")
        parent.append(child)

        assert parent[0] is child

    def test_is_visible(self):
        # Visible by default
        node = Node(tag="div")
        assert node.is_visible() is True

        # display: none
        node = Node(tag="div", styles={"display": "none"})
        assert node.is_visible() is False

        # visibility: hidden
        node = Node(tag="div", styles={"visibility": "hidden"})
        assert node.is_visible() is False

        # opacity: 0
        node = Node(tag="div", styles={"opacity": "0"})
        assert node.is_visible() is False

        # opacity: 1
        node = Node(tag="div", styles={"opacity": "1"})
        assert node.is_visible() is True

    def test_has_zero_size(self):
        # No bounds
        node = Node(tag="div")
        assert node.has_zero_size() is False

        # Normal size
        node = Node(tag="div", bounds=BoundingBox(0, 0, 100, 50))
        assert node.has_zero_size() is False

        # Zero width
        node = Node(tag="div", bounds=BoundingBox(0, 0, 0, 50))
        assert node.has_zero_size() is True

        # Zero height
        node = Node(tag="div", bounds=BoundingBox(0, 0, 100, 0))
        assert node.has_zero_size() is True

    def test_get_text(self):
        parent = Node(tag="div")
        parent.append(Text("Hello "))

        child = Node(tag="span")
        child.append(Text("world"))
        parent.append(child)

        parent.append(Text("!"))

        assert parent.get_text() == "Hello world!"

    def test_get_text_with_separator(self):
        parent = Node(tag="div")
        parent.append(Text("Line 1"))
        parent.append(Text("Line 2"))

        assert parent.get_text(separator="\n") == "Line 1\nLine 2"


class TestText:
    """Tests for Text."""

    def test_create_text(self):
        text = Text("Hello world")
        assert text.content == "Hello world"
        assert text.parent is None

    def test_str(self):
        text = Text("Hello")
        assert str(text) == "Hello"
