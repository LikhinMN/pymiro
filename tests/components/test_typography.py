from pymiro.components.typography import Heading, Text, Code, Link

def test_heading_level_maps_to_font_size():
    node = Heading("Title", level=2)
    assert "font-size: 24px" in node.props["style"]
    
def test_text_bold_italic_props_pass_through():
    node = Text("Hello", bold=True, italic=True)
    assert "font-weight: bold" in node.props["style"]
    assert "font-style: italic" in node.props["style"]

def test_code_uses_monospace_font():
    node = Code("print(1)")
    assert "font-family: monospace" in node.props["style"]

def test_link_on_click_prop_wires():
    called = False
    def on_click():
        nonlocal called
        called = True
        
    node = Link("Click me", on_click=on_click)
    node.props["on_click"]()
    assert called
