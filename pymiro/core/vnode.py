"""
VNode structures for pymiro.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class VNode:
    """A lightweight representation of a UI node."""
    type: str
    props: dict[str, Any]
    children: list[VNode | str]
    key: str | None = None

def _create_vnode(type_: str, children: tuple[VNode | str, ...], props: dict[str, Any]) -> VNode:
    key = props.pop("key", None)
    return VNode(type=type_, props=props, children=list(children), key=key)

def Div(*children: VNode | str, **props: Any) -> VNode:
    """Create a Div VNode."""
    return _create_vnode("div", children, props)

def Text(content: str, **props: Any) -> VNode:
    """Create a Text VNode."""
    return _create_vnode("text", (content,), props)

def Button(label: str, **props: Any) -> VNode:
    """Create a Button VNode."""
    props["label"] = label
    return _create_vnode("button", (), props)

def Input(**props: Any) -> VNode:
    """Create an Input VNode."""
    return _create_vnode("input", (), props)

def Row(*children: VNode | str, **props: Any) -> VNode:
    """Create a Row VNode."""
    return _create_vnode("row", children, props)

def Col(*children: VNode | str, **props: Any) -> VNode:
    """Create a Col VNode."""
    return _create_vnode("col", children, props)

__all__ = ["VNode", "Div", "Text", "Button", "Input", "Row", "Col"]
