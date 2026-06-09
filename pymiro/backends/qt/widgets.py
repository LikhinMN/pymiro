"""
Qt widget mappings for pymiro.
"""
from typing import Any
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QSizePolicy, QGridLayout, QProgressBar, QComboBox, 
    QCheckBox, QSlider, QTabWidget
)
from PySide6.QtCore import Qt

def create_widget(vnode_type: str) -> Any:
    widget: Any
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
    elif vnode_type == "col" or vnode_type == "stack":
        widget = QFrame()
        layout_c: QVBoxLayout = QVBoxLayout()
        layout_c.setContentsMargins(0, 0, 0, 0)
        layout_c.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(layout_c)
    elif vnode_type == "grid":
        widget = QFrame()
        layout_g = QGridLayout()
        layout_g.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout_g)
    elif vnode_type == "text":
        widget = QLabel()
    elif vnode_type == "button":
        widget = QPushButton()
    elif vnode_type == "input":
        widget = QLineEdit()
    elif vnode_type == "spacer":
        # We return an empty QWidget configured as a spacer
        # This prevents issues with QSpacerItem not being a QWidget
        widget = QWidget()
        widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    elif vnode_type == "divider":
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.HLine)
        widget.setFrameShadow(QFrame.Shadow.Sunken)
    elif vnode_type == "spinner":
        widget = QProgressBar()
        widget.setMaximum(0) # indeterminate
        widget.setMinimum(0)
    elif vnode_type == "progressbar":
        widget = QProgressBar()
    elif vnode_type == "select":
        widget = QComboBox()
    elif vnode_type == "checkbox":
        widget = QCheckBox()
    elif vnode_type == "slider":
        widget = QSlider(Qt.Orientation.Horizontal)
    elif vnode_type == "tabs":
        widget = QTabWidget()
    elif vnode_type == "badge":
        widget = QLabel()
    else:
        raise ValueError(f"Unknown vnode type: {vnode_type}")

    if isinstance(widget, QWidget):
        if isinstance(widget, (QPushButton, QLineEdit, QCheckBox, QComboBox)):
            widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        elif vnode_type == "spacer":
            pass # keep Expanding
        else:
            widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
    return widget

def apply_prop(widget: Any, key: str, value: Any) -> None:
    if key in ("text", "label", "children"):
        if isinstance(widget, (QLabel, QPushButton, QCheckBox)):
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
    elif key == "width":
        if value == "full":
            policy = widget.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
            widget.setSizePolicy(policy)
    elif key == "spacing":
        layout = widget.layout()
        if layout is not None:
            layout.setSpacing(int(value))
    elif key == "padding":
        layout = widget.layout()
        if layout is not None:
            v = int(value)
            layout.setContentsMargins(v, v, v, v)
    elif key == "align":
        layout = widget.layout()
        if layout is not None:
            if value == "left":
                layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            elif value == "right":
                layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            elif value == "center":
                layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            elif value == "top":
                layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            elif value == "bottom":
                layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
    elif key == "cols" and hasattr(widget, "setProperty"):
        # Store cols as a dynamic property for renderer to use
        widget.setProperty("grid_cols", int(value))
    elif key == "thickness" and isinstance(widget, QFrame):
        widget.setLineWidth(int(value))
    elif key == "checked" and isinstance(widget, QCheckBox):
        widget.setChecked(bool(value))
    elif key == "options" and isinstance(widget, QComboBox):
        widget.blockSignals(True)
        widget.clear()
        widget.addItems([str(opt) for opt in value])
        widget.blockSignals(False)
    elif key == "value":
        if isinstance(widget, QComboBox):
            widget.setCurrentText(str(value))
        elif isinstance(widget, QSlider):
            widget.setValue(int(value))
        elif isinstance(widget, QProgressBar):
            widget.setValue(int(value))
        elif isinstance(widget, QLineEdit):
            if widget.text() != str(value):
                widget.setText(str(value))
    elif key == "min" and isinstance(widget, QSlider):
        widget.setMinimum(int(value))
    elif key == "max" and isinstance(widget, QSlider):
        widget.setMaximum(int(value))
    elif key == "step" and isinstance(widget, QSlider):
        widget.setSingleStep(int(value))
    elif key == "tabs" and isinstance(widget, QTabWidget):
        # We don't add pages here because tabs are VNodes.
        # Wait, the prompt says "Tabs: Props: tabs: list[str]".
        # We need to add empty tabs with titles.
        widget.clear()
        for t in value:
            widget.addTab(QWidget(), str(t))
    elif key == "active" and isinstance(widget, QTabWidget):
        widget.setCurrentIndex(int(value))

def remove_prop(widget: Any, key: str) -> None:
    if key in ("text", "label", "children"):
        if isinstance(widget, (QLabel, QPushButton, QLineEdit, QCheckBox)):
            widget.setText("")
    elif key == "placeholder" and isinstance(widget, QLineEdit):
        widget.setPlaceholderText("")
    elif key == "disabled":
        widget.setEnabled(True)
    elif key == "style":
        widget.setStyleSheet("")
    elif key == "stretch":
        widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    elif key == "width":
        policy = widget.sizePolicy()
        if isinstance(widget, (QPushButton, QLineEdit, QCheckBox, QComboBox)):
            policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        else:
            policy.setHorizontalPolicy(QSizePolicy.Policy.Preferred)
        widget.setSizePolicy(policy)
    elif key == "spacing":
        layout = widget.layout()
        if layout is not None:
            layout.setSpacing(0)
    elif key == "padding":
        layout = widget.layout()
        if layout is not None:
            layout.setContentsMargins(0, 0, 0, 0)
    elif key == "thickness" and isinstance(widget, QFrame):
        widget.setLineWidth(1)
    elif key == "tabs" and isinstance(widget, QTabWidget):
        widget.clear()

__all__ = ["create_widget", "apply_prop", "remove_prop"]
