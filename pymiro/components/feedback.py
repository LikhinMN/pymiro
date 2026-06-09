"""
Feedback components for pymiro.
"""
import asyncio
from typing import Any

from pymiro.core.component import component, use_signal, use_effect
from pymiro.core.vnode import VNode
from pymiro.components.layout import _build_props

from pymiro.theme.provider import use_theme

@component
def Toast(
    message: str,
    variant: str = "info",
    duration: int = 3000,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    theme = use_theme()
    visible = use_signal(True)
    
    def auto_hide() -> Any:
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
        
    c = theme.colors
    s = {
        "padding": f"{theme.spacing.sm}px {theme.spacing.lg}px", 
        "border-radius": f"{theme.radius.lg}px", 
        "color": c.text_primary,
        "background-color": c.surface,
        "border": f"1px solid {c.border}"
    }
    
    if variant == "success":
        s["background-color"] = c.success
        s["color"] = c.success_text
        s["border"] = f"1px solid {c.success}"
    elif variant == "warning":
        s["background-color"] = c.warning
        s["color"] = c.warning_text
        s["border"] = f"1px solid {c.warning}"
    elif variant == "error":
        s["background-color"] = c.error
        s["color"] = c.error_text
        s["border"] = f"1px solid {c.error}"
    else:
        # info
        s["background-color"] = c.info
        s["color"] = c.info_text
        s["border"] = f"1px solid {c.info}"
        
    if style:
        s.update(style)
        
    props = _build_props({"text": message}, s, class_name)
    return VNode(type="text", props=props, children=[], key=key)

@component
def Spinner(
    size: int = 24,
    color: str | None = None,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    theme = use_theme()
    _c = color if color is not None else theme.colors.primary
    s = {"min-width": f"{size}px", "min-height": f"{size}px", "max-width": f"{size}px", "max-height": f"{size}px"}
    if style:
        s.update(style)
    s["color"] = _c
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
    theme = use_theme()
    c = theme.colors
    t = theme.typography
    s = {
        "padding": f"2px {theme.spacing.sm}px", 
        "border-radius": f"{theme.radius.xl}px", 
        "font-size": f"{t.size_xs}px", 
        "font-weight": str(t.weight_bold), 
        "color": c.text_primary,
        "background-color": c.surface
    }
    
    if variant == "success":
        s["background-color"] = c.success
        s["color"] = c.success_text
    elif variant == "warning":
        s["background-color"] = c.warning
        s["color"] = c.warning_text
    elif variant == "error":
        s["background-color"] = c.error
        s["color"] = c.error_text
    else:
        s["background-color"] = c.info
        s["color"] = c.info_text
        
    if style:
        s.update(style)
        
    props = _build_props({"text": text}, s, class_name)
    return VNode(type="badge", props=props, children=[], key=key)

@component
def ProgressBar(
    value: float,
    color: str | None = None,
    height: int = 8,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None
) -> VNode:
    # Progress bar styling is mainly handled by QSS, but we can emit a chunk color property 
    # or just rely on QSS entirely if color is None.
    clamped_value = max(0, min(100, int(value)))
    s = {"min-height": f"{height}px", "max-height": f"{height}px"}
    if color is not None:
        # Actually it's hard to set chunk color dynamically without updating QSS, 
        # but let's just pass what we can or assume QSS handles it.
        pass
        
    if style:
        s.update(style)
    props = _build_props({"value": clamped_value}, s, class_name)
    return VNode(type="progressbar", props=props, children=[], key=key)
