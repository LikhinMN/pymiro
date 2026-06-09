# pymiro

> Signal-native, declarative GUI framework for Python.

[![PyPI](https://img.shields.io/pypi/v/pymiro)](https://pypi.org/project/pymiro)
[![Python](https://img.shields.io/pypi/pyversions/pymiro)](https://pypi.org/project/pymiro)
[![License](https://img.shields.io/pypi/l/pymiro)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-119%20passing-brightgreen)]()

## What is pymiro?

pymiro is a modern GUI framework for Python that brings web-like declarative syntax and fine-grained reactivity to the desktop. Inspired by SolidJS, it uses a signal-based reactivity engine and a keyed virtual DOM to efficiently update Qt widgets (PySide6) without relying on heavy class hierarchies or complex event bindings. 

## Why pymiro?

| Feature | tkinter | PyQt6 / PySide6 | pymiro |
|---|---|---|---|
| Declarative | ❌ | ❌ | ✅ |
| Reactive signals | ❌ | ❌ | ✅ |
| Component model | ❌ | ❌ | ✅ |
| Hot reload | ❌ | ❌ | ✅ |
| Theming | ❌ | manual | ✅ |
| Type safe | ❌ | partial | ✅ |

## Installation

```bash
pip install pymiro
```

Requires Python 3.12+

## Quick start

```python
import sys
from PySide6.QtWidgets import QApplication
from pymiro.core import signal, component, effect
from pymiro.elements import Window, VBox, Text, Button
from pymiro.renderer import render

@component
def Counter():
    count, set_count = signal(0)
    
    return Window(title="pymiro Counter")(
        VBox()(
            Text(text=lambda: f"Count: {count()}"),
            Button(text="Increment", on_click=lambda: set_count(count() + 1)),
            Button(text="Decrement", on_click=lambda: set_count(count() - 1))
        )
    )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    render(Counter(), None)
    sys.exit(app.exec())
```

## Core concepts

### Signals
Signals are the primitives of reactivity in pymiro. They track state and automatically update any components or effects that depend on them.

```python
from pymiro.core import signal, computed

count, set_count = signal(5)
double_count = computed(lambda: count() * 2)

print(double_count()) # 10
set_count(10)
print(double_count()) # 20
```

### Components
Components in pymiro are simple functions decorated with `@component` that return virtual nodes representing the UI.

```python
from pymiro.core import component
from pymiro.elements import VBox, Text

@component
def Greeting(name: str):
    return VBox()(
        Text(text=f"Hello, {name}!")
    )
```

### Theming
pymiro includes a built-in design token system and light/dark themes that can be applied to your application easily.

```python
from pymiro.theme import ThemeProvider, DarkTheme
from pymiro.elements import Window

@component
def App():
    return ThemeProvider(theme=DarkTheme())(
        Window()(
            # Your components here...
        )
    )
```

## Project status

Alpha — API may change before 1.0.0.
Check out our [Roadmap](https://github.com/LikhinMN/pymiro/issues).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up the project and run tests.

## License

MIT