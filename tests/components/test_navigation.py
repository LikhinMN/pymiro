from pymiro.components.navigation import Tabs, Sidebar

def test_tabs_renders_correct_tab_count():
    node = Tabs(tabs=["Home", "Profile", "Settings"])
    assert node.props["tabs"] == ["Home", "Profile", "Settings"]

def test_tabs_on_change():
    called_with = None
    def on_change(i):
        nonlocal called_with
        called_with = i
        
    node = Tabs(tabs=["A", "B"], on_change=on_change)
    node.props["on_change"](1)
    assert called_with == 1

def test_sidebar_active_prop_highlights_item():
    node = Sidebar(items=["Dash", "Users"], active=1)
    # Sidebar returns a Stack. Its children are Buttons.
    assert node.type == "stack"
    children = node.children
    assert len(children) == 2
    
    # Dash is index 0 (not active)
    assert "transparent" in children[0].props["style"] # ghost variant
    
    # Users is index 1 (active)
    assert "background-color: #0066cc" in children[1].props["style"] # primary variant
