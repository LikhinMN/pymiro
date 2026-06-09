from pymiro.components.input import Button, TextInput, Checkbox, Select, Slider

def test_button_variants_produce_correct_style():
    node_primary = Button("Submit", variant="primary", on_click=lambda: None)
    assert "background-color: #0066cc" in node_primary.props["style"]
    
    node_danger = Button("Delete", variant="danger", on_click=lambda: None)
    assert "background-color: #dc3545" in node_danger.props["style"]

def test_button_disabled_prop():
    node = Button("Click", disabled=True, on_click=lambda: None)
    assert node.props["disabled"] is True

def test_textinput_on_change_wires():
    called_with = None
    def on_change(v):
        nonlocal called_with
        called_with = v
        
    node = TextInput(value="", on_change=on_change)
    node.props["on_change"]("hello")
    assert called_with == "hello"

def test_checkbox_on_change():
    called_with = None
    def on_change(v):
        nonlocal called_with
        called_with = v
        
    node = Checkbox(checked=False, on_change=on_change)
    node.props["on_change"](True)
    assert called_with is True

def test_select_options_prop():
    node = Select(options=["A", "B"])
    assert node.props["options"] == ["A", "B"]

def test_slider_props_pass_through():
    node = Slider(min=10, max=50, step=5)
    assert node.props["min"] == 10
    assert node.props["max"] == 50
    assert node.props["step"] == 5
