"""
Layout components for pymiro.
"""
from typing import Any

from pymiro.core.component import component
from pymiro.core.vnode import VNode

def _build_props(
    base: dict[str, Any],
    style: dict[str, str] | None,
    class_name: str | None
) -> dict[str, Any]:
    if style:
        # Convert dict to QSS string
        s = "; ".join(f"{k}: {v}" for k, v in style.items())
        if base.get("style"):
            base["style"] += f"; {s}"
        else:
            base["style"] = s
    if class_name:
        base["class"] = class_name
    return base

@component
def Stack(
    *children: VNode | str | None,
    spacing: int = 8,
    padding: int = 0,
    align: str = "left",
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    props = _build_props({"spacing": spacing, "padding": padding, "align": align}, style, class_name)
    # Filter out Nones
    valid_children = [c for c in children if c is not None]
    return VNode(type="stack", props=props, children=valid_children, key=key)

@component
def Row(
    *children: VNode | str | None,
    spacing: int = 8,
    padding: int = 0,
    align: str = "left",
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    props = _build_props({"spacing": spacing, "padding": padding, "align": align}, style, class_name)
    valid_children = [c for c in children if c is not None]
    return VNode(type="row", props=props, children=valid_children, key=key)

@component
def Grid(
    *children: VNode | str | None,
    cols: int = 2,
    spacing: int = 8,
    padding: int = 0,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    props = _build_props({"cols": cols, "spacing": spacing, "padding": padding}, style, class_name)
    valid_children = [c for c in children if c is not None]
    return VNode(type="grid", props=props, children=valid_children, key=key)

@component
def Spacer(
    size: int | None = None,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    props = _build_props({}, style, class_name)
    if size is not None:
        # For spacer, if size is given, we fix the width/height depending on layout (hard to know).
        # We'll just apply min-width and min-height
        props["style"] = props.get("style", "") + f"; min-width: {size}px; min-height: {size}px"
    return VNode(type="spacer", props=props, children=[], key=key)

@component
def Divider(
    color: str = "#e0e0e0",
    thickness: int = 1,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    props = _build_props({"thickness": thickness}, style, class_name)
    props["style"] = props.get("style", "") + f"; background-color: {color}"
    return VNode(type="divider", props=props, children=[], key=key)
