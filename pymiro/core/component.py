"""
Component decorator and hooks for pymiro.
"""

import functools
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any, TypeVar, cast

from pymiro.core.signals import Computed, Signal, computed, effect, signal
from pymiro.core.vnode import VNode

F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")


class ComponentError(Exception):
    """Raised for component-related errors."""

    pass


_is_in_component: ContextVar[bool] = ContextVar("_is_in_component", default=False)
_current_disposers: ContextVar[list[Callable[[], None]]] = ContextVar(
    "_current_disposers"
)
_component_states: ContextVar[dict[Callable[..., Any], list[Any]]] = ContextVar(
    "_component_states"
)
_current_component: ContextVar[Callable[..., Any] | None] = ContextVar(
    "_current_component", default=None
)
_hook_index: ContextVar[int] = ContextVar("_hook_index", default=0)


def component[F: Callable[..., Any]](fn: F) -> F:
    """
    Wrap a function into a pymiro component.
    Validates that the component returns a VNode.
    """

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        prev_is_in = _is_in_component.get()
        prev_comp = _current_component.get()
        prev_idx = _hook_index.get()

        try:
            states = _component_states.get()
        except LookupError:
            states = {}
            _component_states.set(states)

        _is_in_component.set(True)
        _current_component.set(fn)
        _hook_index.set(0)

        if fn not in states:
            states[fn] = []

        disposers: list[Callable[[], None]] = []
        token_disp = _current_disposers.set(disposers)

        try:
            result = fn(*args, **kwargs)
        finally:
            _is_in_component.set(prev_is_in)
            _current_component.set(prev_comp)
            _hook_index.set(prev_idx)
            _current_disposers.reset(token_disp)

        if not isinstance(result, VNode):
            raise ComponentError(f"Component {fn.__name__} must return a VNode")

        # Add cleanup to VNode or store it somewhere? Wait!
        # The prompt says: "Effect cleanup: are use_effect disposers actually called on component unmount, or are they registered but never invoked?"
        # Where can we store the disposers?
        # We can store them in a special field on VNode or in a global registry keyed by the node_id.
        # But wait! We don't have node_id in the component!
        # What if we store the disposers in a closure in the VNode's props?
        # A hidden prop `__disposers__`!
        if disposers:
            result.props["__disposers__"] = disposers

        return result

    setattr(wrapper, "__pymiro_component__", True)
    return cast(F, wrapper)


def use_signal[T](initial: T) -> Signal[T]:
    """
    Create a reactive signal within a component.
    """
    if not _is_in_component.get():
        raise ComponentError("use_signal must be called inside a component")

    comp = _current_component.get()
    idx = _hook_index.get()

    if comp is not None:
        try:
            states = _component_states.get()
        except LookupError:
            states = {}
            _component_states.set(states)

        state_list = states[comp]
        if idx >= len(state_list):
            state_list.append(signal(initial))
        sig = state_list[idx]
        _hook_index.set(idx + 1)
        return cast(Signal[T], sig)

    return signal(initial)


def use_computed[T](fn: Callable[[], T]) -> Computed[T]:
    """
    Create a computed reactive value within a component.
    """
    if not _is_in_component.get():
        raise ComponentError("use_computed must be called inside a component")
    return computed(fn)


def use_effect(fn: Callable[[], None]) -> None:
    """
    Create a side effect within a component.
    """
    if not _is_in_component.get():
        raise ComponentError("use_effect must be called inside a component")
    dispose = effect(fn)
    try:
        disposers = _current_disposers.get()
        disposers.append(dispose)
    except LookupError:
        pass


__all__ = ["component", "use_signal", "use_computed", "use_effect", "ComponentError"]
