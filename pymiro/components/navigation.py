"""
Navigation components for pymiro.
"""

from collections.abc import Callable
from typing import Any

from pymiro.components.input import Button
from pymiro.components.layout import Stack, _build_props
from pymiro.core.component import component
from pymiro.core.vnode import VNode
from pymiro.theme.provider import use_theme


@component
def Tabs(
    tabs: list[str],
    active: int = 0,
    on_change: Callable[[int], Any] | None = None,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    use_theme()
    props = _build_props({"tabs": tabs, "active": active}, style, class_name)
    if on_change is not None:
        props["on_change"] = on_change
    return VNode(type="tabs", props=props, children=[], key=key)


@component
def Sidebar(
    items: list[str],
    active: int = 0,
    on_change: Callable[[int], Any] | None = None,
    width: int = 200,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    theme = use_theme()
    buttons = []
    for i, item in enumerate(items):
        is_active = i == active

        # We need to capture `i` carefully in the lambda
        def make_handler(idx: int) -> Callable[[], None]:
            def handler() -> None:
                if on_change is not None:
                    on_change(idx)

            return handler

        btn = Button(
            label=item,
            on_click=make_handler(i),
            variant="primary" if is_active else "ghost",
            full_width=True,
        )
        buttons.append(btn)

    s = {
        "min-width": f"{width}px",
        "max-width": f"{width}px",
        "background-color": theme.colors.surface,
        "border-right": f"1px solid {theme.colors.border}",
        "height": "100%",
    }
    if style:
        s.update(style)

    # We wrap in Stack
    return Stack(
        *buttons,
        spacing=theme.spacing.xs,
        padding=theme.spacing.sm,
        style=s,
        class_name=class_name,
        key=key,
    )
