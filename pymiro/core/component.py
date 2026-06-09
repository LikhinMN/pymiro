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
_current_disposers: ContextVar[list[Callable[[], None]]] = ContextVar("_current_disposers")
_component_states: dict[Callable[..., Any], list[Any]] = {}
_current_component: ContextVar[Callable[..., Any] | None] = ContextVar("_current_component", default=None)
_hook_index: ContextVar[int] = ContextVar("_hook_index", default=0)

def component(fn: F) -> F:
    """
    Wrap a function into a pymiro component.
    Validates that the component returns a VNode.
    """
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        prev_is_in = _is_in_component.get()
        prev_comp = _current_component.get()
        prev_idx = _hook_index.get()
        
        _is_in_component.set(True)
        _current_component.set(fn)
        _hook_index.set(0)
        
        if fn not in _component_states:
            _component_states[fn] = []
            
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
        return result

    setattr(wrapper, "__pymiro_component__", True)
    return cast(F, wrapper)


def use_signal(initial: T) -> Signal[T]:
    """
    Create a reactive signal within a component.
    """
    if not _is_in_component.get():
        raise ComponentError("use_signal must be called inside a component")
        
    comp = _current_component.get()
    idx = _hook_index.get()
    
    if comp is not None:
        state_list = _component_states[comp]
        if idx >= len(state_list):
            state_list.append(signal(initial))
        sig = state_list[idx]
        _hook_index.set(idx + 1)
        return cast(Signal[T], sig)
        
    return signal(initial)


def use_computed(fn: Callable[[], T]) -> Computed[T]:
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
