"""
Qt widget mappings for pymiro.
"""
from typing import Any
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QSizePolicy
from PySide6.QtCore import Qt

def create_widget(vnode_type: str) -> QWidget:
    widget: QWidget
    if vnode_type == "div":
        widget = QFrame()
        layout_v: QVBoxLayout = QVBoxLayout()
        layout_v.setContentsMargins(0, 0, 0, 0)
        layout_v.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(layout_v)
    elif vnode_type == "row":
        widget = QFrame()
        layout_h: QHBoxLayout = QHBoxLayout()
        layout_h.setContentsMargins(0, 0, 0, 0)
        layout_h.setAlignment(Qt.AlignmentFlag.AlignLeft)
        widget.setLayout(layout_h)
    elif vnode_type == "col":
        widget = QFrame()
        layout_c: QVBoxLayout = QVBoxLayout()
        layout_c.setContentsMargins(0, 0, 0, 0)
        layout_c.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(layout_c)
    elif vnode_type == "text":
        widget = QLabel()
    elif vnode_type == "button":
        widget = QPushButton()
    elif vnode_type == "input":
        widget = QLineEdit()
    else:
        raise ValueError(f"Unknown vnode type: {vnode_type}")

    widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    return widget

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
    elif key == "stretch":
        if value:
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        else:
            widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

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
    elif key == "stretch":
        widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

__all__ = ["create_widget", "apply_prop", "remove_prop"]
