"""
Reactive signal primitives for pymiro.
"""
import contextlib
from collections.abc import Callable, Generator
from contextvars import ContextVar
from typing import Any, Generic, Protocol, TypeVar, cast, overload

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)

class CycleError(Exception):
    """Raised when a cyclical dependency is detected in computed signals or effects."""
    pass

class _Publisher(Protocol):
    def _add_subscriber(self, subscriber: "_Subscriber") -> None: ...
    def _remove_subscriber(self, subscriber: "_Subscriber") -> None: ...

class _Subscriber(Protocol):
    def _notify(self) -> None: ...
    def _add_dependency(self, publisher: _Publisher) -> None: ...

_current_tracking_context: ContextVar[_Subscriber | None] = ContextVar("_current_tracking_context", default=None)
_evaluation_stack: ContextVar[tuple[Any, ...]] = ContextVar("_evaluation_stack", default=())
_batch_depth: ContextVar[int] = ContextVar("_batch_depth", default=0)
_batched_effects: ContextVar[set["_Effect"]] = ContextVar("_batched_effects", default=set())

class Signal(Protocol[T]):
    """Protocol for a reactive signal."""
    def __call__(self) -> T: ...
    def set(self, value: T) -> None: ...
    def peek(self) -> T: ...

class Computed(Protocol[T_co]):
    """Protocol for a derived reactive value."""
    def __call__(self) -> T_co: ...

class _Signal(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value
        self._subscribers: set[_Subscriber] = set()

    def __call__(self) -> T:
        subscriber = _current_tracking_context.get()
        if subscriber is not None:
            self._add_subscriber(subscriber)
            subscriber._add_dependency(self)
        return self._value

    def set(self, value: T) -> None:
        if self._value == value:
            return
        self._value = value
        with _batch_cm():
            subs = list(self._subscribers)
            for sub in subs:
                sub._notify()

    def peek(self) -> T:
        return self._value

    def _add_subscriber(self, subscriber: _Subscriber) -> None:
        self._subscribers.add(subscriber)

    def _remove_subscriber(self, subscriber: _Subscriber) -> None:
        self._subscribers.discard(subscriber)


class _Computed(Generic[T]):
    def __init__(self, fn: Callable[[], T]) -> None:
        self._fn = fn
        self._value: T | None = None
        self._dirty = True
        self._subscribers: set[_Subscriber] = set()
        self._dependencies: set[_Publisher] = set()

    def __call__(self) -> T:
        current_stack = _evaluation_stack.get()
        if self in current_stack:
            names = []
            for item in current_stack + (self,):
                if hasattr(item, '_fn'):
                    names.append(getattr(item._fn, '__name__', str(item)))
                else:
                    names.append(str(item))
            raise CycleError(f"Cycle detected: {' -> '.join(names)}")

        if self._dirty:
            for dep in self._dependencies:
                dep._remove_subscriber(self)
            self._dependencies.clear()

            prev_context = _current_tracking_context.get()
            _current_tracking_context.set(self)
            _evaluation_stack.set(current_stack + (self,))

            try:
                self._value = self._fn()
                self._dirty = False
            finally:
                _evaluation_stack.set(current_stack)
                _current_tracking_context.set(prev_context)

        subscriber = _current_tracking_context.get()
        if subscriber is not None:
            self._add_subscriber(subscriber)
            subscriber._add_dependency(self)

        return cast(T, self._value)

    def _notify(self) -> None:
        if not self._dirty:
            self._dirty = True
            subs = list(self._subscribers)
            for sub in subs:
                sub._notify()

    def _add_subscriber(self, subscriber: _Subscriber) -> None:
        self._subscribers.add(subscriber)

    def _remove_subscriber(self, subscriber: _Subscriber) -> None:
        self._subscribers.discard(subscriber)

    def _add_dependency(self, publisher: _Publisher) -> None:
        self._dependencies.add(publisher)


class _Effect:
    def __init__(self, fn: Callable[[], None]) -> None:
        self._fn = fn
        self._dependencies: set[_Publisher] = set()
        self._active = True
        self._run()

    def _run(self) -> None:
        if not self._active:
            return

        current_stack = _evaluation_stack.get()
        if self in current_stack:
            names = []
            for item in current_stack + (self,):
                if hasattr(item, '_fn'):
                    names.append(getattr(item._fn, '__name__', str(item)))
                else:
                    names.append(str(item))
            raise CycleError(f"Cycle detected: {' -> '.join(names)}")

        for dep in self._dependencies:
            dep._remove_subscriber(self)
        self._dependencies.clear()

        prev_context = _current_tracking_context.get()
        _current_tracking_context.set(self)
        _evaluation_stack.set(current_stack + (self,))

        try:
            self._fn()
        finally:
            _evaluation_stack.set(current_stack)
            _current_tracking_context.set(prev_context)

    def _notify(self) -> None:
        if not self._active:
            return
        if _batch_depth.get() > 0:
            _batched_effects.get().add(self)
        else:
            self._run()

    def _add_dependency(self, publisher: _Publisher) -> None:
        self._dependencies.add(publisher)

    def dispose(self) -> None:
        self._active = False
        for dep in self._dependencies:
            dep._remove_subscriber(self)
        self._dependencies.clear()


@contextlib.contextmanager
def _batch_cm() -> Generator[None, Any, None]:
    depth = _batch_depth.get()
    _batch_depth.set(depth + 1)
    if depth == 0:
        _batched_effects.set(set())
    try:
        yield
    finally:
        _batch_depth.set(depth)
        if depth == 0:
            while True:
                effects = _batched_effects.get()
                if not effects:
                    break
                _batched_effects.set(set())
                for eff in effects:
                    if getattr(eff, '_active', True):
                        eff._run()


def signal(value: T) -> Signal[T]:
    """
    Create a reactive signal holding a value.
    
    Returns a Signal object which can be called to read its value,
    or updated using the .set() method.
    """
    return _Signal(value)


def computed(fn: Callable[[], T]) -> Computed[T]:
    """
    Create a reactive computed value derived from other signals.
    
    The computed value auto-tracks dependencies and lazily recomputes
    only when a dependency changes.
    """
    return _Computed(fn)


def effect(fn: Callable[[], None]) -> Callable[[], None]:
    """
    Run a function immediately and re-run it when its dependencies change.
    
    Returns a disposer function. Calling the disposer stops the effect
    from re-running and cleans up subscriptions.
    """
    e = _Effect(fn)
    return e.dispose


@overload
def batch(fn: Callable[[], T]) -> T: ...

@overload
def batch() -> contextlib.AbstractContextManager[None]: ...

def batch(fn: Callable[[], T] | None = None) -> Any:
    """
    Batch multiple signal updates so that effects only run once
    after the batch completes.
    
    Can be used as a context manager `with batch():` or as a higher-order
    function `batch(fn)`.
    """
    if fn is not None:
        with _batch_cm():
            return fn()
    return _batch_cm()

__all__ = ["signal", "computed", "effect", "batch", "CycleError", "Signal", "Computed"]
