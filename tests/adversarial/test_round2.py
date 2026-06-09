import pytest
from pymiro.core.vnode import VNode
from pymiro.core.reconciler import reconcile, CreateNode, DestroyNode, UpdateProps, MoveNode, ReconcilerError

def Div(*children: VNode | str, **props):
    key = props.pop("key", None)
    return VNode("div", props, list(children), key=key)

def Text(text: str, **props):
    key = props.pop("key", None)
    return VNode("text", {**props, "text": text}, [], key=key)

def test_keyed_list_reversal():
    old = Div(
        Text("a", key="a"),
        Text("b", key="b"),
        Text("c", key="c"),
    )
    new = Div(
        Text("c", key="c"),
        Text("b", key="b"),
        Text("a", key="a"),
    )
    patches = reconcile(old, new)
    create_count = sum(1 for p in patches if isinstance(p, CreateNode))
    destroy_count = sum(1 for p in patches if isinstance(p, DestroyNode))
    assert create_count == 0
    assert destroy_count == 0

def test_keyed_list_mixed():
    old = Div(Text("a", key="a"), Text("b"))
    new = Div(Text("a", key="a"), Text("c"))
    with pytest.raises(ReconcilerError):
        reconcile(old, new)

def test_deeply_nested_signal_update():
    old = Div(
        Div(Div(Text("deep", key="d1"))),
        Div(Text("sibling", key="s1")),
    )
    new = Div(
        Div(Div(Text("changed", key="d1"))),
        Div(Text("sibling", key="s1")),
    )
    patches = reconcile(old, new)
    update_patches = [p for p in patches if isinstance(p, UpdateProps)]
    assert len(update_patches) == 1

def test_1000_keyed_children_reorder():
    import random
    keys = [str(i) for i in range(1000)]
    children_old = [Text(k, key=k) for k in keys]
    shuffled = keys.copy()
    random.shuffle(shuffled)
    children_new = [Text(k, key=k) for k in shuffled]

    old = Div(*children_old)
    new = Div(*children_new)

    patches = reconcile(old, new)
    assert all(not isinstance(p, CreateNode) for p in patches)
    assert all(not isinstance(p, DestroyNode) for p in patches)

def test_reconcile_is_pure():
    old = Div(Text("hello"))
    new = Div(Text("world"))
    reconcile(old, new)
    assert old.children[0].props["text"] == "hello"
