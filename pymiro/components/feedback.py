"""
Feedback components for pymiro.
"""
import asyncio
from typing import Any

from pymiro.core.component import component, use_signal, use_effect
from pymiro.core.vnode import VNode
from pymiro.components.layout import _build_props

@component
def Toast(
    message: str,
    variant: str = "info",
    duration: int = 3000,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    visible = use_signal(True)
    
    def auto_hide() -> Any:
        # Re-run effect only when duration changes. 
        # Actually it runs once per mount unless duration changes (we don't have dependency arrays though)
        # So we just do:
        task = asyncio.create_task(asyncio.sleep(duration / 1000.0))
        
        def on_done(t: asyncio.Task[Any]) -> None:
            if not t.cancelled():
                visible.set(False)
                
        task.add_done_callback(on_done)
        
        def dispose() -> None:
            task.cancel()
        return dispose
        
    use_effect(auto_hide)
    
    if not visible():
        return VNode("spacer", {"style": "display: none"}, [], key)
        
    s = {"padding": "12px 24px", "border-radius": "8px", "color": "white"}
    if variant == "success":
        s["background-color"] = "#28a745"
    elif variant == "warning":
        s["background-color"] = "#ffc107"
        s["color"] = "black"
    elif variant == "error":
        s["background-color"] = "#dc3545"
    else:
        # info
        s["background-color"] = "#17a2b8"
        
    if style:
        s.update(style)
        
    props = _build_props({"text": message}, s, class_name)
    return VNode(type="text", props=props, children=[], key=key)

@component
def Spinner(
    size: int = 24,
    color: str = "#0066cc",
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    s = {"min-width": f"{size}px", "min-height": f"{size}px", "max-width": f"{size}px", "max-height": f"{size}px"}
    if style:
        s.update(style)
    # Qt doesn't directly support color on QProgressBar spinner without complex QSS, but we'll apply it
    # in style anyway.
    s["color"] = color
    props = _build_props({}, s, class_name)
    return VNode(type="spinner", props=props, children=[], key=key)

@component
def Badge(
    text: str,
    variant: str = "info",
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    s = {"padding": "4px 8px", "border-radius": "12px", "font-size": "12px", "font-weight": "bold", "color": "white"}
    if variant == "success":
        s["background-color"] = "#28a745"
    elif variant == "warning":
        s["background-color"] = "#ffc107"
        s["color"] = "black"
    elif variant == "error":
        s["background-color"] = "#dc3545"
    else:
        s["background-color"] = "#17a2b8"
        
    if style:
        s.update(style)
        
    props = _build_props({"text": text}, s, class_name)
    return VNode(type="badge", props=props, children=[], key=key)

@component
def ProgressBar(
    value: float,
    color: str = "#0066cc",
    height: int = 8,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    clamped_value = max(0, min(100, int(value)))
    s = {"min-height": f"{height}px", "max-height": f"{height}px"}
    if style:
        s.update(style)
    props = _build_props({"value": clamped_value}, s, class_name)
    return VNode(type="progressbar", props=props, children=[], key=key)
