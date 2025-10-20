"""Tests for semantic filters."""

import pytest
from domnode.node import Node, Text
from domnode.filters.semantic import (
    filter_attributes,
    filter_empty,
    collapse_single_child_wrappers,
    filter_presentational_roles,
    SEMANTIC_ATTRIBUTES,
)


class TestFilterAttributes:
    """Tests for filter_attributes."""

    def test_keep_semantic_attributes(self):
        node = Node(
            tag="button",
            attrib={
                "role": "button",
                "aria-label": "Submit",
                "class": "btn",
                "id": "submit-btn",
            },
        )

        filtered = filter_attributes(node)
        assert "role" in filtered.attrib
        assert "aria-label" in filtered.attrib
        assert "class" not in filtered.attrib
        assert "id" not in filtered.attrib

    def test_remove_all_non_semantic_attributes(self):
        node = Node(tag="div", attrib={"class": "container", "id": "main", "data-test": "value"})

        filtered = filter_attributes(node)
        assert len(filtered.attrib) == 0

    def test_custom_keep_set(self):
        node = Node(tag="div", attrib={"class": "foo", "id": "bar", "role": "button"})
        filtered = filter_attributes(node, keep={"class", "id"})

        assert "class" in filtered.attrib
        assert "id" in filtered.attrib
        assert "role" not in filtered.attrib

    def test_nested_filter_attributes(self):
        parent = Node(tag="div", attrib={"class": "parent", "role": "navigation"})
        child = Node(tag="button", attrib={"class": "btn", "aria-label": "Click"})
        parent.append(child)

        filtered = filter_attributes(parent)
        assert "role" in filtered.attrib
        assert "class" not in filtered.attrib
        assert "aria-label" in filtered.children[0].attrib
        assert "class" not in filtered.children[0].attrib

    def test_keep_text_nodes(self):
        parent = Node(tag="div")
        parent.append(Text("Hello"))

        filtered = filter_attributes(parent)
        assert len(filtered.children) == 1
        assert isinstance(filtered.children[0], Text)
        assert filtered.children[0].content == "Hello"


class TestFilterEmpty:
    """Tests for filter_empty."""

    def test_remove_empty_div(self):
        parent = Node(tag="section")
        parent.append(Node(tag="div"))  # Empty, no attributes, no children
        parent.append(Node(tag="p", attrib={"role": "text"}))

        filtered = filter_empty(parent)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "p"

    def test_keep_node_with_attributes(self):
        node = Node(tag="div", attrib={"role": "button"})
        filtered = filter_empty(node)
        assert filtered is not None

    def test_keep_node_with_children(self):
        parent = Node(tag="div")
        child = Node(tag="span", attrib={"role": "text"})  # Non-empty child
        parent.append(child)
        filtered = filter_empty(parent)
        assert filtered is not None
        assert len(filtered.children) == 1

    def test_keep_interactive_tags_even_if_empty(self):
        button = Node(tag="button")  # No attributes, no children
        filtered = filter_empty(button)
        assert filtered is not None

        input_node = Node(tag="input")
        filtered = filter_empty(input_node)
        assert filtered is not None

    def test_remove_empty_text_nodes(self):
        parent = Node(tag="div")
        parent.append(Text("   "))  # Whitespace only
        parent.append(Text("Hello"))

        filtered = filter_empty(parent)
        assert len(filtered.children) == 1
        assert filtered.children[0].content == "Hello"

    def test_nested_empty_removal(self):
        root = Node(tag="div")
        child = Node(tag="span")
        child.append(Node(tag="div"))  # Empty
        child.append(Node(tag="p", attrib={"role": "text"}))
        root.append(child)

        filtered = filter_empty(root)
        assert len(filtered.children[0].children) == 1

    def test_return_none_if_root_is_empty(self):
        div = Node(tag="div")  # No attributes, no children, not interactive
        filtered = filter_empty(div)
        assert filtered is None


class TestCollapseWrappers:
    """Tests for collapse_single_child_wrappers."""

    def test_collapse_single_child_wrapper(self):
        wrapper = Node(tag="div")  # No attributes
        child = Node(tag="button", attrib={"role": "button"})
        wrapper.append(child)

        collapsed = collapse_single_child_wrappers(wrapper)
        assert collapsed.tag == "button"
        assert collapsed.attrib["role"] == "button"

    def test_keep_wrapper_with_attributes(self):
        wrapper = Node(tag="div", attrib={"role": "navigation"})
        child = Node(tag="button")
        wrapper.append(child)

        collapsed = collapse_single_child_wrappers(wrapper)
        assert collapsed.tag == "div"
        assert collapsed.attrib["role"] == "navigation"

    def test_keep_wrapper_with_multiple_children(self):
        wrapper = Node(tag="div")
        wrapper.append(Node(tag="button"))
        wrapper.append(Node(tag="button"))

        collapsed = collapse_single_child_wrappers(wrapper)
        assert collapsed.tag == "div"
        assert len(collapsed.children) == 2

    def test_keep_wrapper_with_text_content(self):
        wrapper = Node(tag="div")
        wrapper.append(Text("Label: "))
        wrapper.append(Node(tag="button"))

        collapsed = collapse_single_child_wrappers(wrapper)
        assert collapsed.tag == "div"

    def test_nested_collapse(self):
        outer = Node(tag="div")
        middle = Node(tag="div")
        inner = Node(tag="button", attrib={"role": "button"})
        middle.append(inner)
        outer.append(middle)

        collapsed = collapse_single_child_wrappers(outer)
        # Should collapse all the way to button
        assert collapsed.tag == "button"

    def test_keep_text_nodes(self):
        parent = Node(tag="div", attrib={"role": "group"})
        parent.append(Text("Hello"))

        collapsed = collapse_single_child_wrappers(parent)
        assert len(collapsed.children) == 1
        assert isinstance(collapsed.children[0], Text)

    def test_dont_collapse_with_whitespace_only_text(self):
        wrapper = Node(tag="div")
        wrapper.append(Text("   "))  # Whitespace
        wrapper.append(Node(tag="button"))

        collapsed = collapse_single_child_wrappers(wrapper)
        # Should collapse because whitespace is not meaningful
        assert collapsed.tag == "button"


class TestFilterPresentationalRoles:
    """Tests for filter_presentational_roles."""

    def test_remove_role_none(self):
        node = Node(tag="div", attrib={"role": "none", "class": "wrapper"})
        filtered = filter_presentational_roles(node)
        assert "role" not in filtered.attrib
        assert "class" in filtered.attrib

    def test_remove_role_presentation(self):
        node = Node(tag="ul", attrib={"role": "presentation"})
        filtered = filter_presentational_roles(node)
        assert "role" not in filtered.attrib

    def test_case_insensitive(self):
        node1 = Node(tag="div", attrib={"role": "NONE"})
        node2 = Node(tag="div", attrib={"role": "Presentation"})
        
        filtered1 = filter_presentational_roles(node1)
        filtered2 = filter_presentational_roles(node2)
        
        assert "role" not in filtered1.attrib
        assert "role" not in filtered2.attrib

    def test_keep_other_roles(self):
        node = Node(tag="div", attrib={"role": "button"})
        filtered = filter_presentational_roles(node)
        assert filtered.attrib.get("role") == "button"

    def test_keep_structure_with_list(self):
        # Important: preserve list structure even with role="none"
        ul = Node(tag="ul", attrib={"role": "none"})
        li1 = Node(tag="li")
        li1.append(Text("Item 1"))
        li2 = Node(tag="li")
        li2.append(Text("Item 2"))
        ul.append(li1)
        ul.append(li2)
        
        filtered = filter_presentational_roles(ul)
        assert filtered.tag == "ul"
        assert "role" not in filtered.attrib
        assert len(filtered.children) == 2
        assert filtered.children[0].tag == "li"
        assert filtered.children[1].tag == "li"

    def test_nested_presentational_roles(self):
        parent = Node(tag="div", attrib={"role": "none"})
        child = Node(tag="span", attrib={"role": "presentation"})
        parent.append(child)
        
        filtered = filter_presentational_roles(parent)
        assert "role" not in filtered.attrib
        assert "role" not in filtered.children[0].attrib

    def test_keep_text_nodes(self):
        parent = Node(tag="div", attrib={"role": "none"})
        parent.append(Text("Hello"))
        
        filtered = filter_presentational_roles(parent)
        assert len(filtered.children) == 1
        assert isinstance(filtered.children[0], Text)
        assert filtered.children[0].content == "Hello"

    def test_mixed_roles_in_tree(self):
        root = Node(tag="div", attrib={"role": "main"})
        child1 = Node(tag="div", attrib={"role": "none"})
        child2 = Node(tag="div", attrib={"role": "button"})
        root.append(child1)
        root.append(child2)
        
        filtered = filter_presentational_roles(root)
        assert filtered.attrib.get("role") == "main"
        assert "role" not in filtered.children[0].attrib
        assert filtered.children[1].attrib.get("role") == "button"

    def test_no_role_attribute(self):
        node = Node(tag="div", attrib={"class": "container"})
        filtered = filter_presentational_roles(node)
        assert "role" not in filtered.attrib
        assert "class" in filtered.attrib
