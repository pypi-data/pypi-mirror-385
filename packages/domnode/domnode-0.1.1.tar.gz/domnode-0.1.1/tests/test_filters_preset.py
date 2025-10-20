"""Tests for preset filters."""

import pytest
from domnode.node import Node, Text, BoundingBox
from domnode.filters.preset import filter_visible, filter_semantic, filter_all


class TestFilterVisible:
    """Tests for filter_visible preset."""

    def test_remove_all_visibility_issues(self):
        root = Node(tag="div")
        root.append(Node(tag="script"))  # Non-visible tag
        root.append(Node(tag="div", styles={"display": "none"}))  # CSS hidden
        root.append(Node(tag="div", bounds=BoundingBox(0, 0, 0, 0)))  # Zero size
        root.append(Node(tag="button", bounds=BoundingBox(0, 0, 100, 50)))  # Visible

        filtered = filter_visible(root)
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_cascading_filters(self):
        # Test that filters are applied in order
        root = Node(tag="div")
        hidden_script = Node(tag="script", styles={"display": "block"})  # Script tag
        root.append(hidden_script)
        root.append(Node(tag="button"))

        filtered = filter_visible(root)
        # Script should be removed by non_visible_tags filter first
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"

    def test_return_none_if_all_removed(self):
        div = Node(tag="div", styles={"display": "none"})
        filtered = filter_visible(div)
        assert filtered is None

    def test_nested_visibility_filtering(self):
        root = Node(tag="div")
        child = Node(tag="section")
        child.append(Node(tag="script"))
        child.append(Node(tag="style"))
        child.append(Node(tag="button"))
        root.append(child)

        filtered = filter_visible(root)
        assert len(filtered.children[0].children) == 1
        assert filtered.children[0].children[0].tag == "button"


class TestFilterSemantic:
    """Tests for filter_semantic preset."""

    def test_apply_all_semantic_filters(self):
        # Create wrapper with non-semantic attributes
        wrapper = Node(tag="div", attrib={"class": "wrapper", "role": "navigation"})
        empty_div = Node(tag="div", attrib={"id": "empty"})
        button = Node(tag="button", attrib={"class": "btn", "role": "button"})

        wrapper.append(empty_div)
        wrapper.append(button)

        filtered = filter_semantic(wrapper)

        # Wrapper should not be collapsed (has semantic attribute)
        # Should remove non-semantic attributes
        assert filtered.tag == "div"
        assert "role" in filtered.attrib
        assert "class" not in filtered.attrib
        # Should remove empty div
        assert len(filtered.children) == 1
        # Button should only have role
        assert "role" in filtered.children[0].attrib
        assert "class" not in filtered.children[0].attrib

    def test_collapse_nested_wrappers(self):
        outer = Node(tag="div")
        middle = Node(tag="div")
        inner = Node(tag="button", attrib={"role": "button"})
        middle.append(inner)
        outer.append(middle)

        filtered = filter_semantic(outer)
        # Should collapse to button
        assert filtered.tag == "button"
        assert filtered.attrib["role"] == "button"

    def test_return_none_if_empty_after_filtering(self):
        div = Node(tag="div", attrib={"class": "empty"})
        filtered = filter_semantic(div)
        # After removing attributes, it's empty and not interactive
        assert filtered is None


class TestFilterAll:
    """Tests for filter_all preset."""

    def test_apply_both_visibility_and_semantic_filters(self):
        root = Node(tag="div", attrib={"class": "container", "role": "main"})
        root.append(Node(tag="script"))  # Non-visible
        root.append(Node(tag="div", styles={"display": "none"}))  # CSS hidden
        root.append(Node(tag="div", attrib={"id": "empty"}))  # Empty
        wrapper = Node(tag="div")
        button = Node(tag="button", attrib={"class": "btn", "role": "button"})
        wrapper.append(button)
        root.append(wrapper)

        filtered = filter_all(root)

        # Should remove: script, hidden div, empty div
        # Should collapse: wrapper (no attributes)
        # Should remove: non-semantic attributes
        # Root should keep semantic role attribute
        assert filtered.tag == "div"
        assert "role" in filtered.attrib
        assert "class" not in filtered.attrib
        assert len(filtered.children) == 1
        assert filtered.children[0].tag == "button"
        assert "role" in filtered.children[0].attrib
        assert "class" not in filtered.children[0].attrib

    def test_comprehensive_filtering(self):
        html = Node(tag="html", attrib={"lang": "en"})  # Add semantic attribute
        head = Node(tag="head")
        head.append(Node(tag="script"))
        head.append(Node(tag="style"))

        body = Node(tag="body", attrib={"class": "page"})
        nav = Node(tag="nav", attrib={"id": "nav", "role": "navigation"})

        hidden = Node(tag="div", styles={"display": "none"})
        nav.append(hidden)

        wrapper1 = Node(tag="div", attrib={"class": "wrapper1"})
        wrapper2 = Node(tag="div", attrib={"class": "wrapper2"})
        link = Node(tag="a", attrib={"href": "/home", "class": "link", "aria-label": "Home"})
        wrapper2.append(link)
        wrapper1.append(wrapper2)
        nav.append(wrapper1)

        body.append(nav)
        html.append(head)
        html.append(body)

        filtered = filter_all(html)

        # Head should be removed (non-visible tag)
        # Body should have only nav
        # Nav should have only the link (hidden removed, wrappers collapsed)
        # Only semantic attributes should remain

        # HTML wrapper gets collapsed since only body remains and body gets collapsed to nav
        # So final result is nav
        assert filtered.tag == "nav"
        assert "role" in filtered.attrib
        assert "id" not in filtered.attrib

        # Wrappers should be collapsed, link should be direct child
        assert len(filtered.children) == 1
        link_filtered = filtered.children[0]
        assert link_filtered.tag == "a"
        assert "href" in link_filtered.attrib
        assert "aria-label" in link_filtered.attrib
        assert "class" not in link_filtered.attrib

    def test_return_none_if_all_removed(self):
        div = Node(tag="div", styles={"display": "none"}, attrib={"class": "hidden"})
        filtered = filter_all(div)
        assert filtered is None

    def test_order_matters(self):
        # Visibility filtering happens before semantic filtering
        root = Node(tag="div", attrib={"role": "main"})  # Add semantic attribute
        script = Node(tag="script", attrib={"role": "script"})  # Has semantic attr
        root.append(script)

        filtered = filter_all(root)
        # Script should be removed by visibility filter before semantic sees it
        # Root should remain with semantic attribute
        assert filtered is not None
        assert filtered.tag == "div"
        assert "role" in filtered.attrib
        assert len(filtered.children) == 0
