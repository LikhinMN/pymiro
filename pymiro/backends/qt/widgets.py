"""
Qt widget mappings for pymiro.
"""
from typing import Any
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit

def create_widget(vnode_type: str) -> QWidget:
    if vnode_type == "div":
        frame = QFrame()
        layout_v: QVBoxLayout = QVBoxLayout()
        layout_v.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(layout_v)
        return frame
    elif vnode_type == "row":
        frame = QFrame()
        layout_h: QHBoxLayout = QHBoxLayout()
        layout_h.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(layout_h)
        return frame
    elif vnode_type == "col":
        frame = QFrame()
        layout_c: QVBoxLayout = QVBoxLayout()
        layout_c.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(layout_c)
        return frame
    elif vnode_type == "text":
        return QLabel()
    elif vnode_type == "button":
        return QPushButton()
    elif vnode_type == "input":
        return QLineEdit()
    else:
        raise ValueError(f"Unknown vnode type: {vnode_type}")

def apply_prop(widget: QWidget, key: str, value: Any) -> None:
    if key in ("text", "label", "children"):
        if isinstance(widget, (QLabel, QPushButton)):
            if isinstance(value, list) and value and isinstance(value[0], str):
                widget.setText("".join(value))
            elif isinstance(value, str):
                widget.setText(value)
        elif isinstance(widget, QLineEdit):
            if isinstance(value, str):
                widget.setText(value)
    elif key == "placeholder" and isinstance(widget, QLineEdit):
        widget.setPlaceholderText(str(value))
    elif key == "disabled":
        widget.setEnabled(not value)
    elif key == "style":
        widget.setStyleSheet(str(value))

def remove_prop(widget: QWidget, key: str) -> None:
    if key in ("text", "label", "children"):
        if isinstance(widget, (QLabel, QPushButton, QLineEdit)):
            widget.setText("")
    elif key == "placeholder" and isinstance(widget, QLineEdit):
        widget.setPlaceholderText("")
    elif key == "disabled":
        widget.setEnabled(True)
    elif key == "style":
        widget.setStyleSheet("")

__all__ = ["create_widget", "apply_prop", "remove_prop"]
