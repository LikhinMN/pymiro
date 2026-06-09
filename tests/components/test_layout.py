from pymiro.components.layout import Stack, Row, Grid, Spacer, Divider
from pymiro.core.vnode import VNode

def test_stack_renders_with_spacing_prop():
    node = Stack(VNode("text", {}, []), spacing=16)
    assert node.type == "stack"
    assert node.props["spacing"] == 16
    assert node.props["padding"] == 0
    assert node.props["align"] == "left"

def test_row_renders_children_horizontally():
    node = Row(VNode("text", {}, []), spacing=8)
    assert node.type == "row"
    assert node.props["spacing"] == 8

def test_grid_accepts_cols_prop():
    node = Grid(VNode("text", {}, []), cols=3)
    assert node.type == "grid"
    assert node.props["cols"] == 3

def test_spacer_renders_with_size_prop():
    node = Spacer(size=40)
    assert node.type == "spacer"
    assert "min-width: 40px" in node.props["style"]
    assert "min-height: 40px" in node.props["style"]

def test_divider_renders_with_color_prop():
    node = Divider(color="#ff0000")
    assert node.type == "divider"
    assert "background-color: #ff0000" in node.props["style"]
