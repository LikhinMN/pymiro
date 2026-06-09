"""
Input components for pymiro.
"""
from typing import Callable, Any

from pymiro.core.component import component
from pymiro.core.vnode import VNode
from pymiro.components.layout import _build_props

@component
def Button(
    label: str,
    on_click: Callable[..., Any],
    variant: str = "default",
    disabled: bool = False,
    full_width: bool = False,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    s = {"padding": "6px 12px", "border-radius": "4px"}
    if variant == "primary":
        s.update({"background-color": "#0066cc", "color": "white", "border": "1px solid #005bb5"})
    elif variant == "danger":
        s.update({"background-color": "#dc3545", "color": "white", "border": "1px solid #c82333"})
    elif variant == "ghost":
        s.update({"background-color": "transparent", "border": "none"})
    else:
        # default
        s.update({"background-color": "white", "color": "black", "border": "1px solid #cccccc"})
        
    if style:
        s.update(style)
        
    width = "full" if full_width else "auto"
        
    props = _build_props({
        "label": label, 
        "on_click": on_click, 
        "disabled": disabled,
        "width": width
    }, s, class_name)
    return VNode(type="button", props=props, children=[], key=key)

@component
def TextInput(
    value: str = "",
    placeholder: str = "",
    on_change: Callable[[str], Any] | None = None,
    disabled: bool = False,
    full_width: bool = True,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    s = {"padding": "6px", "border": "1px solid #cccccc", "border-radius": "4px"}
    if style:
        s.update(style)
        
    width = "full" if full_width else "auto"
        
    props = _build_props({
        "value": value,
        "placeholder": placeholder,
        "disabled": disabled,
        "width": width
    }, s, class_name)
    
    if on_change is not None:
        props["on_change"] = on_change
        
    return VNode(type="input", props=props, children=[], key=key)

@component
def Checkbox(
    checked: bool = False,
    label: str = "",
    on_change: Callable[[bool], Any] | None = None,
    disabled: bool = False,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    props = _build_props({
        "checked": checked,
        "text": label,
        "disabled": disabled
    }, style, class_name)
    
    if on_change is not None:
        props["on_change"] = on_change
        
    return VNode(type="checkbox", props=props, children=[], key=key)

@component
def Select(
    options: list[str],
    value: str = "",
    on_change: Callable[[str], Any] | None = None,
    disabled: bool = False,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    props = _build_props({
        "options": options,
        "value": value,
        "disabled": disabled
    }, style, class_name)
    
    if on_change is not None:
        props["on_change"] = on_change
        
    return VNode(type="select", props=props, children=[], key=key)

@component
def Slider(
    value: float = 0,
    min: float = 0,
    max: float = 100,
    step: float = 1,
    on_change: Callable[[float], Any] | None = None,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    props = _build_props({
        "value": value,
        "min": min,
        "max": max,
        "step": step
    }, style, class_name)
    
    if on_change is not None:
        # Wrap on_change because slider passes int usually (or we can just pass through)
        props["on_change"] = on_change
        
    return VNode(type="slider", props=props, children=[], key=key)
