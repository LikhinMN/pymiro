from pymiro.core.vnode import VNode, Div, Text, Button, Input, Row, Col

def test_div_creates_vnode():
    node = Div()
    assert isinstance(node, VNode)
    assert node.type == "div"
    assert node.children == []
    assert node.props == {}
    assert node.key is None

def test_button_stores_label_in_props():
    node = Button("Click Me", disabled=True)
    assert node.type == "button"
    assert node.props["label"] == "Click Me"
    assert node.props["disabled"] is True
    assert node.children == []

def test_text_stores_content_in_children():
    node = Text("Hello World", color="red")
    assert node.type == "text"
    assert node.children == ["Hello World"]
    assert node.props["color"] == "red"

def test_key_extracted_to_vnode_key():
    node = Div(key="main-div", className="container")
    assert node.key == "main-div"
    assert "key" not in node.props
    assert node.props["className"] == "container"

def test_nested_children():
    node = Div(Row(Button("OK")), Text("Cancel"))
    assert node.type == "div"
    assert len(node.children) == 2
    row = node.children[0]
    text = node.children[1]
    
    assert isinstance(row, VNode)
    assert row.type == "row"
    assert len(row.children) == 1
    assert isinstance(row.children[0], VNode)
    assert row.children[0].type == "button"
    assert row.children[0].props["label"] == "OK"
    
    assert isinstance(text, VNode)
    assert text.type == "text"
    assert text.children == ["Cancel"]

def test_props_passed_through_correctly():
    node = Input(placeholder="Type here", type="password")
    assert node.type == "input"
    assert node.props["placeholder"] == "Type here"
    assert node.props["type"] == "password"

def test_col_creates_vnode():
    node = Col(Text("Item 1"), Text("Item 2"), key="col-1")
    assert node.type == "col"
    assert node.key == "col-1"
    assert len(node.children) == 2
