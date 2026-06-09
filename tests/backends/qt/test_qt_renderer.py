import pytest
from PySide6.QtWidgets import QLabel, QPushButton, QLineEdit
from pymiro.core.vnode import Div, Text, Button
from pymiro.core.reconciler import CreateNode, UpdateProps, DestroyNode, SetChildren, MoveNode
from pymiro.backends.qt.renderer import QtRenderer
from pymiro.app import App
from pymiro.core.component import component, use_signal
from pymiro.core.signals import effect
from pymiro.core.reconciler import reconcile

def test_create_adds_widget_to_registry(qtbot):
    renderer = QtRenderer()
    renderer.create("node1", "text", {"children": ["hello"]}, None)
    assert "node1" in renderer.registry
    widget = renderer.registry["node1"]
    assert isinstance(widget, QLabel)
    assert widget.text() == "hello"

def test_create_with_parent_id_adds_to_layout(qtbot):
    renderer = QtRenderer()
    renderer.create("parent1", "div", {}, None)
    renderer.create("child1", "button", {"label": "click"}, "parent1")
    parent = renderer.registry["parent1"]
    layout = parent.layout()
    assert layout is not None
    assert layout.count() == 1
    assert layout.itemAt(0).widget() == renderer.registry["child1"]

def test_update_applies_changed_props(qtbot):
    renderer = QtRenderer()
    renderer.create("node1", "input", {"placeholder": "old"}, None)
    widget = renderer.registry["node1"]
    assert widget.placeholderText() == "old"
    
    renderer.update("node1", {"placeholder": "new"}, [])
    assert widget.placeholderText() == "new"

def test_destroy_removes_widget(qtbot):
    renderer = QtRenderer()
    renderer.create("parent1", "div", {}, None)
    renderer.create("child1", "text", {"children": ["hi"]}, "parent1")
    
    layout = renderer.registry["parent1"].layout()
    assert layout.count() == 1
    
    renderer.destroy("child1")
    assert "child1" not in renderer.registry
    assert layout.count() == 0

def test_set_children_reorders_widgets(qtbot):
    renderer = QtRenderer()
    renderer.create("parent1", "div", {}, None)
    renderer.create("childA", "text", {"children": ["A"]}, "parent1")
    renderer.create("childB", "text", {"children": ["B"]}, "parent1")
    
    layout = renderer.registry["parent1"].layout()
    assert layout.itemAt(0).widget() == renderer.registry["childA"]
    
    renderer.set_children("parent1", ["childB", "childA"])
    assert layout.itemAt(0).widget() == renderer.registry["childB"]
    assert layout.itemAt(1).widget() == renderer.registry["childA"]

def test_bind_event_connects_clicked(qtbot):
    renderer = QtRenderer()
    renderer.create("btn1", "button", {"label": "Click"}, None)
    
    clicked = False
    def on_click():
        nonlocal clicked
        clicked = True
        
    renderer.bind_event("btn1", "on_click", on_click)
    btn = renderer.registry["btn1"]
    
    from PySide6.QtCore import Qt
    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
    assert clicked

def test_commit_applies_patches(qtbot):
    renderer = QtRenderer()
    patches = [
        CreateNode("parent1", "div", {}, None),
        CreateNode("child1", "text", {"children": ["init"]}, "parent1"),
        UpdateProps("child1", {"children": ["new"]}, [])
    ]
    renderer.commit(patches)
    # commit uses queued connection, we need to process events
    qtbot.wait(10)
    assert renderer.registry["child1"].text() == "new"

def test_full_integration(qtbot):
    @component
    def Counter():
        count = use_signal(0)
        return Div(
            Text(f"Count: {count()}"),
            Button("Increment", on_click=lambda: count.set(count() + 1))
        )
        
    renderer = QtRenderer()
    
    current_tree = None
    def render_cycle():
        nonlocal current_tree
        new_tree = Counter()
        patches = reconcile(current_tree, new_tree)
        renderer.commit(patches)
        current_tree = new_tree
        
    effect(render_cycle)
    
    qtbot.wait(10) # process initial render events
    
    label = renderer.registry["root:0:0"]
    btn = renderer.registry["root:0:1"]
    
    assert isinstance(label, QLabel)
    assert isinstance(btn, QPushButton)
    assert label.text() == "Count: 0"
    
    from PySide6.QtCore import Qt
    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
    qtbot.wait(10) # process next render events
    
    assert label.text() == "Count: 1"
