"""
Typography components for pymiro.
"""

from collections.abc import Callable
from typing import Any

from pymiro.components.layout import _build_props
from pymiro.core.component import component
from pymiro.core.vnode import VNode
from pymiro.theme.provider import use_theme


@component
def Heading(
    text: str,
    level: int = 1,
    color: str | None = None,
    bold: bool = True,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Heading component.

    Args:
        text: Configuration for text.
        level: Configuration for level.
        color: Configuration for color.
        bold: Configuration for bold.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Heading

        Heading()
        ```
    """
    theme = use_theme()
    t = theme.typography
    size = {1: t.size_3xl, 2: t.size_2xl, 3: t.size_xl, 4: t.size_md}.get(
        level, t.size_3xl
    )
    _c = color if color is not None else theme.colors.text_primary

    s = {"font-size": f"{size}px", "color": _c}
    if bold:
        s["font-weight"] = str(t.weight_bold)

    if style:
        s.update(style)

    props = _build_props({"text": text}, s, class_name)
    return VNode(type="text", props=props, children=[], key=key)


@component
def Text(
    text: str,
    size: int | None = None,
    color: str | None = None,
    bold: bool = False,
    italic: bool = False,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Text component.

    Args:
        text: Configuration for text.
        size: Configuration for size.
        color: Configuration for color.
        bold: Configuration for bold.
        italic: Configuration for italic.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Text

        Text()
        ```
    """
    theme = use_theme()
    t = theme.typography
    _s = size if size is not None else t.size_md
    _c = color if color is not None else theme.colors.text_primary

    s = {"font-size": f"{_s}px", "color": _c}
    if bold:
        s["font-weight"] = str(t.weight_bold)
    if italic:
        s["font-style"] = "italic"

    if style:
        s.update(style)

    props = _build_props({"text": text}, s, class_name)
    return VNode(type="text", props=props, children=[], key=key)


@component
def Code(
    text: str,
    size: int | None = None,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Code component.

    Args:
        text: Configuration for text.
        size: Configuration for size.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Code

        Code()
        ```
    """
    theme = use_theme()
    t = theme.typography
    _s = size if size is not None else t.size_sm

    s = {
        "font-size": f"{_s}px",
        "font-family": t.font_mono,
        "background-color": theme.colors.surface,
        "color": theme.colors.text_primary,
        "padding": "2px 4px",
        "border-radius": f"{theme.radius.sm}px",
    }
    if style:
        s.update(style)

    props = _build_props({"text": text}, s, class_name)
    return VNode(type="text", props=props, children=[], key=key)


@component
def Link(
    text: str,
    on_click: Callable[..., Any],
    color: str | None = None,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Link component.

    Args:
        text: Configuration for text.
        on_click: Configuration for on_click.
        color: Configuration for color.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Link

        Link()
        ```
    """
    theme = use_theme()
    _c = color if color is not None else theme.colors.primary

    s = {"color": _c, "text-decoration": "underline", "cursor": "pointer"}
    if style:
        s.update(style)

    props = _build_props({"text": text, "on_click": on_click}, s, class_name)
    # Using button for link for proper click handling
    # We strip button styling via CSS
    props["style"] = (
        props.get("style", "")
        + "; border: none; background: transparent; text-align: left; padding: 0;"
    )
    return VNode(type="button", props=props, children=[], key=key)
