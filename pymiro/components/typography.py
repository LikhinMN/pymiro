"""
Typography components for pymiro.
"""
from typing import Callable, Any

from pymiro.core.component import component
from pymiro.core.vnode import VNode
from pymiro.components.layout import _build_props

@component
def Heading(
    text: str,
    level: int = 1,
    color: str = "#000000",
    bold: bool = True,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    size = {1: 32, 2: 24, 3: 18, 4: 14}.get(level, 32)
    s = {"font-size": f"{size}px", "color": color}
    if bold:
        s["font-weight"] = "bold"
        
    if style:
        s.update(style)
        
    props = _build_props({"text": text}, s, class_name)
    return VNode(type="text", props=props, children=[], key=key)

@component
def Text(
    text: str,
    size: int = 14,
    color: str = "#000000",
    bold: bool = False,
    italic: bool = False,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    s = {"font-size": f"{size}px", "color": color}
    if bold:
        s["font-weight"] = "bold"
    if italic:
        s["font-style"] = "italic"
        
    if style:
        s.update(style)
        
    props = _build_props({"text": text}, s, class_name)
    return VNode(type="text", props=props, children=[], key=key)

@component
def Code(
    text: str,
    size: int = 13,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    s = {"font-size": f"{size}px", "font-family": "monospace", "background-color": "#f5f5f5", "padding": "2px 4px"}
    if style:
        s.update(style)
        
    props = _build_props({"text": text}, s, class_name)
    return VNode(type="text", props=props, children=[], key=key)

@component
def Link(
    text: str,
    on_click: Callable[..., Any],
    color: str = "#0066cc",
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    s = {"color": color, "text-decoration": "underline", "cursor": "pointer"}
    if style:
        s.update(style)
        
    props = _build_props({"text": text, "on_click": on_click}, s, class_name)
    # Using button for link for proper click handling
    # We strip button styling via CSS
    props["style"] = props.get("style", "") + "; border: none; background: transparent; text-align: left;"
    return VNode(type="button", props=props, children=[], key=key)
