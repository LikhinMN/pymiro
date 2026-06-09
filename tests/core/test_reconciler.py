import pytest
import asyncio
from pymiro.core.vnode import Div, Text, Button
from pymiro.core.reconciler import (
    reconcile, CreateNode, UpdateProps, DestroyNode, SetChildren, MoveNode, ReconcilerScheduler, Patch
)

def test_initial_mount():
    new = Div(Text("hello"))
    patches = reconcile(None, new)
    assert len(patches) == 3
    assert isinstance(patches[0], CreateNode)
    assert patches[0].type == "div"
    assert isinstance(patches[1], CreateNode)
    assert patches[1].type == "text"
    assert patches[1].props["children"] == ["hello"]
    assert isinstance(patches[2], SetChildren)
    assert patches[2].child_ids == [patches[1].node_id]

def test_no_changes():
    old = Div(Text("hello"))
    new = Div(Text("hello"))
    patches = reconcile(old, new)
    assert patches == []

def test_prop_change():
    old = Div(className="old")
    new = Div(className="new")
    patches = reconcile(old, new)
    assert len(patches) == 1
    assert isinstance(patches[0], UpdateProps)
    assert patches[0].changed == {"className": "new"}
    assert patches[0].removed == []

def test_prop_removed():
    old = Div(className="old", id="main")
    new = Div(id="main")
    patches = reconcile(old, new)
    assert len(patches) == 1
    assert isinstance(patches[0], UpdateProps)
    assert patches[0].changed == {}
    assert patches[0].removed == ["className"]

def test_node_type_change():
    old = Div()
    new = Button("Click")
    patches = reconcile(old, new)
    assert len(patches) == 2
    assert isinstance(patches[0], DestroyNode)
    assert isinstance(patches[1], CreateNode)
    assert patches[1].type == "button"

def test_add_child():
    old = Div(Text("A"))
    new = Div(Text("A"), Text("B"))
    patches = reconcile(old, new)
    assert len(patches) == 2
    assert isinstance(patches[0], CreateNode)
    assert patches[0].type == "text"
    assert patches[0].props["children"] == ["B"]
    assert isinstance(patches[1], SetChildren)

def test_remove_child():
    old = Div(Text("A"), Text("B"))
    new = Div(Text("A"))
    patches = reconcile(old, new)
    assert len(patches) == 2
    assert isinstance(patches[0], DestroyNode)
    assert isinstance(patches[1], SetChildren)
    assert len(patches[1].child_ids) == 1

def test_keyed_reorder():
    old = Div(Div(key="A"), Div(key="B"))
    new = Div(Div(key="B"), Div(key="A"))
    patches = reconcile(old, new)
    assert len(patches) == 2
    assert isinstance(patches[0], MoveNode)
    assert patches[0].node_id.endswith(":A")
    assert isinstance(patches[1], SetChildren)

def test_keyed_add():
    old = Div(Div(key="A"))
    new = Div(Div(key="A"), Div(key="B"))
    patches = reconcile(old, new)
    assert len(patches) == 2
    assert isinstance(patches[0], CreateNode)
    assert patches[0].node_id.endswith(":B")
    assert isinstance(patches[1], SetChildren)

def test_keyed_remove():
    old = Div(Div(key="A"), Div(key="B"))
    new = Div(Div(key="B"))
    patches = reconcile(old, new)
    assert len(patches) == 2
    assert isinstance(patches[0], DestroyNode)
    assert patches[0].node_id.endswith(":A")
    assert isinstance(patches[1], SetChildren)

def test_deep_nested_diff():
    old = Div(Div(Text("A")), Div(Text("B")))
    new = Div(Div(Text("A")), Div(Text("C")))
    patches = reconcile(old, new)
    assert len(patches) == 1
    assert isinstance(patches[0], UpdateProps)
    assert patches[0].changed == {"children": ["C"]}

def test_prompt_example():
    old = Div(Text("hello"))
    new = Div(Text("world"))
    patches = reconcile(old, new)
    assert len(patches) == 1
    assert isinstance(patches[0], UpdateProps)

@pytest.mark.asyncio
async def test_scheduler():
    commits = []
    def on_commit(patches: list[Patch]) -> None:
        commits.append(patches)
        
    scheduler = ReconcilerScheduler(on_commit)
    
    # Schedule two reconciliations
    scheduler.schedule(lambda: reconcile(None, Div()))
    scheduler.schedule(lambda: reconcile(Div(), Div(className="new")))
    
    # Run loop as a background task
    task = asyncio.create_task(scheduler.run_loop())
    
    # Yield control to let it process
    await asyncio.sleep(0.01)
    
    # Cancel task
    task.cancel()
    
    assert len(commits) == 1
    # First batch should contain all patches from both calls
    assert len(commits[0]) == 2
    assert isinstance(commits[0][0], CreateNode)
    assert isinstance(commits[0][1], UpdateProps)
