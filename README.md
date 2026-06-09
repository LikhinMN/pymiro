# pymiro

> A signal-native, declarative GUI framework for Python.

pymiro brings fine-grained reactivity and component-based UI 
to Python desktop applications — inspired by SolidJS, 
built on PySide6.

## Status

Early development. Not ready for use.

## Vision

```python
@component
def Counter():
    count = use_signal(0)
    return Div(
        Text(f"Count: {count()}"),
        Button("Increment", on_click=lambda: count.set(count() + 1))
    )
```

## License

MIT