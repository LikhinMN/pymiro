"""
Reactive signal primitives for pymiro.
"""

import contextlib
import weakref
from collections.abc import Callable, Generator
from contextvars import ContextVar
from typing import Any, Protocol, TypeVar, cast, overload

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class CycleError(Exception):
    """Raised when a cyclical dependency is detected in computed signals or effects."""

    pass


class ComputedSideEffectError(Exception):
    """Raised when an effect is created inside a computed signal."""

    pass


class _Publisher(Protocol):
    def _add_subscriber(self, subscriber: "_Subscriber") -> None: ...
    def _remove_subscriber(self, subscriber: "_Subscriber") -> None: ...


class _Subscriber(Protocol):
    def _notify(self) -> None: ...
    def _add_dependency(self, publisher: _Publisher) -> None: ...


_current_tracking_context: ContextVar[_Subscriber | None] = ContextVar(
    "_current_tracking_context", default=None
)
_evaluation_stack: ContextVar[tuple[Any, ...]] = ContextVar(
    "_evaluation_stack", default=()
)
_batch_depth: ContextVar[int] = ContextVar("_batch_depth", default=0)
_batched_effects: ContextVar[set["_Effect"]] = ContextVar(
    "_batched_effects", default=set()
)
_active_effects: set["_Effect"] = set()


class Signal(Protocol[T]):
    """Protocol for a reactive signal."""

    def __call__(self) -> T: ...
    def set(self, value: T) -> None: ...
    def peek(self) -> T: ...


class Computed(Protocol[T_co]):
    """Protocol for a derived reactive value."""

    def __call__(self) -> T_co: ...


class _Signal[T]:
    def __init__(self, value: T) -> None:
        self._value = value
        self._subscribers: weakref.WeakSet[_Subscriber] = weakref.WeakSet()

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


class _Computed[T]:
    def __init__(self, fn: Callable[[], T]) -> None:
        self._fn = fn
        self._value: T | None = None
        self._dirty = True
        self._subscribers: weakref.WeakSet[_Subscriber] = weakref.WeakSet()
        self._dependencies: set[_Publisher] = set()

    def __call__(self) -> T:
        current_stack = _evaluation_stack.get()
        if self in current_stack:
            names = []
            for item in current_stack + (self,):
                if hasattr(item, "_fn"):
                    names.append(getattr(item._fn, "__name__", str(item)))
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
        if isinstance(_current_tracking_context.get(), _Computed):
            raise ComputedSideEffectError(
                "Cannot create an effect inside a computed signal"
            )

        self._fn = fn
        self._dependencies: set[_Publisher] = set()
        self._active = True
        _active_effects.add(self)
        self._run()

    def _run(self) -> None:
        if not self._active:
            return

        with _batch_cm():
            current_stack = _evaluation_stack.get()
            if self in current_stack:
                names = []
                for item in current_stack + (self,):
                    if hasattr(item, "_fn"):
                        names.append(getattr(item._fn, "__name__", str(item)))
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
        _active_effects.discard(self)
        for dep in self._dependencies:
            dep._remove_subscriber(self)
        self._dependencies.clear()


@contextlib.contextmanager
def _batch_cm() -> Generator[None, Any, None]:
    depth = _batch_depth.get()
    _batch_depth.set(depth + 1)
    if depth == 0:
        _batched_effects.set(set())
    exc_info = None
    try:
        yield
    except BaseException as e:
        exc_info = e
        raise
    finally:
        if depth == 0:
            if exc_info is not None:
                _batch_depth.set(0)
                _batched_effects.set(set())
            else:
                flush_count = 0
                try:
                    while True:
                        effects = _batched_effects.get()
                        if not effects:
                            break
                        flush_count += 1
                        if flush_count > 100:
                            _batched_effects.set(set())
                            raise CycleError(
                                "Maximum batch flush limit exceeded. Cycle detected."
                            )
                        _batched_effects.set(set())
                        for eff in effects:
                            if getattr(eff, "_active", True):
                                eff._run()
                finally:
                    _batch_depth.set(0)
        else:
            _batch_depth.set(depth)


def signal[T](value: T) -> Signal[T]:
    """
    Create a reactive signal holding a value.

    A signal is the core reactive primitive. It holds a value and notifies
    subscribers (like effects or computed values) whenever the value changes.

    Args:
        value: The initial value of the signal.

    Returns:
        Signal: A signal object. Call it `my_signal()` to read the value,
            or `my_signal.set(new_value)` to update it.

    Example:
        ```python
        count = signal(0)
        print(count())  # 0
        
        count.set(1)
        print(count())  # 1
        ```
    """
    return _Signal(value)


def computed[T](fn: Callable[[], T]) -> Computed[T]:
    """
    Create a reactive computed value derived from other signals.

    A computed value automatically tracks which signals it reads. When those
    signals change, the computed value marks itself as dirty and lazily
    re-evaluates only when its value is read again.

    Args:
        fn: A function that computes a value based on signals.

    Returns:
        Computed: A computed object. Call it to read the derived value.

    Example:
        ```python
        first = signal("Hello")
        last = signal("World")
        
        full_name = computed(lambda: f"{first()} {last()}")
        print(full_name())  # "Hello World"
        
        first.set("Hi")
        print(full_name())  # "Hi World"
        ```
    """
    return _Computed(fn)


def effect(fn: Callable[[], None]) -> Callable[[], None]:
    """
    Create a side effect that automatically re-runs when dependencies change.

    The function is run immediately to determine its dependencies. Whenever any
    of the signals read during execution change, the function runs again.

    Args:
        fn: A function containing side effects (e.g., printing, DOM updates).

    Returns:
        Callable: A disposer function. Call it to stop the effect and clean up
            its subscriptions.

    Example:
        ```python
        count = signal(0)
        
        # Runs immediately and prints "Count is 0"
        dispose = effect(lambda: print(f"Count is {count()}"))
        
        count.set(1)  # Automatically prints "Count is 1"
        
        dispose()  # Stop listening
        count.set(2)  # Nothing prints
        ```
    """
    e = _Effect(fn)
    return e.dispose


@overload
def batch[T](fn: Callable[[], T]) -> T: ...


@overload
def batch() -> contextlib.AbstractContextManager[None]: ...


def batch[T](fn: Callable[[], T] | None = None) -> Any:
    """
    Batch multiple signal updates into a single execution frame.

    When you update multiple signals inside a batch, effects depending on those
    signals will only run once after the batch completes, preventing unnecessary
    intermediate renders.

    Can be used as a context manager `with batch():` or as a higher-order
    function `batch(fn)`.

    Args:
        fn: Optional function to run inside the batch.

    Example:
        ```python
        first = signal("John")
        last = signal("Doe")
        
        effect(lambda: print(f"Name: {first()} {last()}"))
        
        with batch():
            first.set("Jane")
            last.set("Smith")
        # Effect only prints "Name: Jane Smith" once
        ```
    """
    if fn is not None:
        with _batch_cm():
            return fn()
    return _batch_cm()


__all__ = [
    "signal",
    "computed",
    "effect",
    "batch",
    "CycleError",
    "ComputedSideEffectError",
    "Signal",
    "Computed",
]
