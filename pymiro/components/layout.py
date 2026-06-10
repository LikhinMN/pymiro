"""
Layout components for pymiro.
"""

from typing import Any

from pymiro.core.component import component
from pymiro.core.vnode import VNode
from pymiro.theme.provider import use_theme


def _build_props(
    base: dict[str, Any], style: dict[str, str] | None, class_name: str | None
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
    spacing: int | None = None,
    padding: int | None = None,
    align: str = "left",
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Stack component.

    Args:
        spacing: Configuration for spacing.
        padding: Configuration for padding.
        align: Configuration for align.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.
        *children: Configuration for *children.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Stack

        Stack()
        ```
    """
    theme = use_theme()
    _sp = spacing if spacing is not None else theme.spacing.sm
    _pd = padding if padding is not None else 0
    props = _build_props(
        {"spacing": _sp, "padding": _pd, "align": align}, style, class_name
    )
    valid_children = [c for c in children if c is not None]
    return VNode(type="stack", props=props, children=valid_children, key=key)


@component
def Row(
    *children: VNode | str | None,
    spacing: int | None = None,
    padding: int | None = None,
    align: str = "left",
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Row component.

    Args:
        spacing: Configuration for spacing.
        padding: Configuration for padding.
        align: Configuration for align.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.
        *children: Configuration for *children.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Row

        Row()
        ```
    """
    theme = use_theme()
    _sp = spacing if spacing is not None else theme.spacing.sm
    _pd = padding if padding is not None else 0
    props = _build_props(
        {"spacing": _sp, "padding": _pd, "align": align}, style, class_name
    )
    valid_children = [c for c in children if c is not None]
    return VNode(type="row", props=props, children=valid_children, key=key)


@component
def Grid(
    *children: VNode | str | None,
    cols: int = 2,
    spacing: int | None = None,
    padding: int | None = None,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Grid component.

    Args:
        cols: Configuration for cols.
        spacing: Configuration for spacing.
        padding: Configuration for padding.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.
        *children: Configuration for *children.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Grid

        Grid()
        ```
    """
    theme = use_theme()
    _sp = spacing if spacing is not None else theme.spacing.sm
    _pd = padding if padding is not None else 0
    props = _build_props(
        {"cols": cols, "spacing": _sp, "padding": _pd}, style, class_name
    )
    valid_children = [c for c in children if c is not None]
    return VNode(type="grid", props=props, children=valid_children, key=key)


@component
def Spacer(
    size: int | None = None,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Spacer component.

    Args:
        size: Configuration for size.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Spacer

        Spacer()
        ```
    """
    use_theme()
    props = _build_props({}, style, class_name)
    if size is not None:
        props["style"] = (
            props.get("style", "") + f"; min-width: {size}px; min-height: {size}px"
        )
    return VNode(type="spacer", props=props, children=[], key=key)


@component
def Divider(
    color: str | None = None,
    thickness: int = 1,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Divider component.

    Args:
        color: Configuration for color.
        thickness: Configuration for thickness.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Divider

        Divider()
        ```
    """
    theme = use_theme()
    _c = color if color is not None else theme.colors.border
    props = _build_props({"thickness": thickness}, style, class_name)
    props["style"] = props.get("style", "") + f"; background-color: {_c}"
    return VNode(type="divider", props=props, children=[], key=key)
