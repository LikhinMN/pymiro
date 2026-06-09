from pymiro.components.typography import Heading, Text, Code, Link

def test_heading_level_maps_to_font_size():
    node = Heading("Title", level=2)
    # Default typography size_2xl is 24px
    assert "font-size: 24px" in node.props["style"]
    
def test_text_bold_italic_props_pass_through():
    node = Text("Hello", bold=True, italic=True)
    # Default bold weight is 700
    assert "font-weight: 700" in node.props["style"]
    assert "font-style: italic" in node.props["style"]

def test_code_uses_monospace_font():
    node = Code("print(1)")
    # Default font_mono is "JetBrains Mono, monospace"
    assert "font-family: JetBrains Mono, monospace" in node.props["style"]

def test_link_on_click_prop_wires():
    called = False
    def on_click():
        nonlocal called
        called = True
        
    node = Link("Click me", on_click=on_click)
    node.props["on_click"]()
    assert called
