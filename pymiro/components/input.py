"""
Input components for pymiro.
"""

from collections.abc import Callable
from typing import Any

from pymiro.components.layout import _build_props
from pymiro.core.component import component
from pymiro.core.vnode import VNode
from pymiro.theme.provider import use_theme


@component
def Button(
    label: str,
    on_click: Callable[..., Any],
    variant: str = "default",
    disabled: bool = False,
    full_width: bool = False,
    style: dict[str, str] | None = None,
    class_name: str | None = None,
    key: str | None = None,
) -> VNode:
    """
    Renders a Button component.

    Args:
        label: Configuration for label.
        on_click: Configuration for on_click.
        variant: Configuration for variant.
        disabled: Configuration for disabled.
        full_width: Configuration for full_width.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Button

        Button()
        ```
    """
    use_theme()
    width = "full" if full_width else "auto"
    props = _build_props(
        {
            "label": label,
            "on_click": on_click,
            "disabled": disabled,
            "width": width,
            "variant": variant,
        },
        style,
        class_name,
    )
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
    key: str | None = None,
) -> VNode:
    """
    Renders a TextInput component.

    Args:
        value: Configuration for value.
        placeholder: Configuration for placeholder.
        on_change: Configuration for on_change.
        disabled: Configuration for disabled.
        full_width: Configuration for full_width.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import TextInput

        TextInput()
        ```
    """
    use_theme()
    width = "full" if full_width else "auto"
    props = _build_props(
        {
            "value": value,
            "placeholder": placeholder,
            "disabled": disabled,
            "width": width,
        },
        style,
        class_name,
    )
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
    key: str | None = None,
) -> VNode:
    """
    Renders a Checkbox component.

    Args:
        checked: Configuration for checked.
        label: Configuration for label.
        on_change: Configuration for on_change.
        disabled: Configuration for disabled.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Checkbox

        Checkbox()
        ```
    """
    use_theme()
    props = _build_props(
        {"checked": checked, "text": label, "disabled": disabled}, style, class_name
    )
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
    key: str | None = None,
) -> VNode:
    """
    Renders a Select component.

    Args:
        options: Configuration for options.
        value: Configuration for value.
        on_change: Configuration for on_change.
        disabled: Configuration for disabled.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Select

        Select()
        ```
    """
    use_theme()
    props = _build_props(
        {"options": options, "value": value, "disabled": disabled}, style, class_name
    )
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
    key: str | None = None,
) -> VNode:
    """
    Renders a Slider component.

    Args:
        value: Configuration for value.
        min: Configuration for min.
        max: Configuration for max.
        step: Configuration for step.
        on_change: Configuration for on_change.
        style: Configuration for style.
        class_name: Configuration for class_name.
        key: Configuration for key.

    Returns:
        VNode: The virtual DOM node representing this component.

    Example:
        ```python
        from pymiro.components import Slider

        Slider()
        ```
    """
    use_theme()
    props = _build_props(
        {"value": value, "min": min, "max": max, "step": step}, style, class_name
    )
    if on_change is not None:
        props["on_change"] = on_change
    return VNode(type="slider", props=props, children=[], key=key)
