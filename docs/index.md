# pymiro

> Signal-native, declarative GUI framework for Python.

pymiro is a modern GUI framework for Python that brings web-like declarative syntax and fine-grained reactivity to the desktop. Inspired by SolidJS, it uses a signal-based reactivity engine and a keyed virtual DOM to efficiently update Qt widgets (PySide6) without relying on heavy class hierarchies or complex event bindings. 

## Features

- **Declarative:** Define your UI as a tree of components, just like HTML or React.
- **Reactive Signals:** State changes automatically trigger surgical updates to only the parts of the UI that depend on that state.
- **Component Model:** Build reusable, composable pieces of UI.
- **Powered by Qt:** Uses PySide6 under the hood for native, performant desktop widgets.

## Installation

```bash
pip install pymiro
```

See the [GitHub Repository](https://github.com/LikhinMN/pymiro) for more details and examples.
