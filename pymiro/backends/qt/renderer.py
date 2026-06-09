"""
Qt Renderer for pymiro.
"""
from typing import Any
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, QMetaObject, Qt, Slot

from pymiro.core.reconciler import CreateNode, UpdateProps, DestroyNode, SetChildren, MoveNode, Patch
from pymiro.backends.qt.widgets import create_widget, apply_prop, remove_prop

class QtRenderer(QObject):
    """
    Implements the Renderer protocol for Qt.
    Mutates Qt widgets based on reconciler patches.
    """
    def __init__(self, root_widget: QWidget | None = None, logger: Any = None) -> None:
        super().__init__()
        self.logger = logger
        self.registry: dict[str, QWidget] = {}
        if root_widget is not None:
            self.registry["root"] = root_widget
        self.event_connections: dict[tuple[str, str], Any] = {}
        self._pending_patches: list[Patch] = []

    def create(
        self,
        node_id: str,
        type: str,
        props: dict[str, Any],
        parent_id: str | None
    ) -> None:
        widget = create_widget(type)
        self.registry[node_id] = widget

        for k, v in props.items():
            if k.startswith("on_"):
                self.bind_event(node_id, k, v)
            else:
                apply_prop(widget, k, v)

        if parent_id is not None:
            parent = self.registry.get(parent_id)
            if parent is not None:
                layout = parent.layout()
                if layout is not None:
                    layout.addWidget(widget)
        else:
            root = self.registry.get("root")
            if root is not None:
                layout = root.layout()
                if layout is not None:
                    layout.addWidget(widget)

    def update(
        self,
        node_id: str,
        changed: dict[str, Any],
        removed: list[str]
    ) -> None:
        widget = self.registry.get(node_id)
        if widget is None:
            return

        for k in removed:
            if k.startswith("on_"):
                self.unbind_event(node_id, k)
            else:
                remove_prop(widget, k)

        for k, v in changed.items():
            if k.startswith("on_"):
                self.bind_event(node_id, k, v)
            else:
                apply_prop(widget, k, v)

    def destroy(self, node_id: str) -> None:
        widget = self.registry.pop(node_id, None)
        if widget is None:
            return
            
        events_to_unbind = [evt for (nid, evt) in list(self.event_connections.keys()) if nid == node_id]
        for evt in events_to_unbind:
            self.unbind_event(node_id, evt)

        parent_widget = widget.parentWidget()
        if parent_widget is not None:
            layout = parent_widget.layout()
            if layout is not None:
                layout.removeWidget(widget)
        
        widget.deleteLater()

    def set_children(
        self,
        parent_id: str,
        child_ids: list[str]
    ) -> None:
        parent = self.registry.get(parent_id)
        if parent is None:
            return
        layout = parent.layout()
        if layout is None:
            return
            
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item is not None:
                w = item.widget()
                if w is not None:
                    layout.removeWidget(w)
                    
        is_grid = hasattr(layout, "addWidget") and parent.property("grid_cols") is not None
        cols = parent.property("grid_cols") or 2
                    
        for idx, cid in enumerate(child_ids):
            child = self.registry.get(cid)
            if child is not None:
                if is_grid:
                    layout.addWidget(child, idx // cols, idx % cols) # type: ignore
                else:
                    layout.addWidget(child)

    def move(
        self,
        node_id: str,
        new_parent_id: str
    ) -> None:
        widget = self.registry.get(node_id)
        new_parent = self.registry.get(new_parent_id)
        if widget is None or new_parent is None:
            return
            
        old_parent = widget.parentWidget()
        if old_parent is not None:
            old_layout = old_parent.layout()
            if old_layout is not None:
                old_layout.removeWidget(widget)
                
        new_layout = new_parent.layout()
        if new_layout is not None:
            is_grid = hasattr(new_layout, "addWidget") and new_parent.property("grid_cols") is not None
            if is_grid:
                # Approximate move appending to the end
                idx = new_layout.count()
                cols = new_parent.property("grid_cols") or 2
                new_layout.addWidget(widget, idx // cols, idx % cols) # type: ignore
            else:
                new_layout.addWidget(widget)

    def bind_event(
        self,
        node_id: str,
        event: str,
        handler: Any
    ) -> None:
        widget = self.registry.get(node_id)
        if widget is None:
            return
            
        if (node_id, event) in self.event_connections:
            # Update the existing wrapper without disconnecting Qt signal
            self.event_connections[(node_id, event)]["state"]["handler"] = handler
            return
            
        state = {"handler": handler}
        
        def wrapper(*args: Any, **kwargs: Any) -> None:
            state["handler"](*args, **kwargs)
            
        from PySide6.QtWidgets import QLineEdit, QCheckBox, QComboBox, QSlider, QTabWidget
            
        conn = None
        if event == "on_click" and hasattr(widget, "clicked"):
            conn = widget.clicked.connect(wrapper)
        elif event == "on_change":
            if isinstance(widget, QLineEdit):
                conn = widget.textChanged.connect(wrapper)
            elif isinstance(widget, QCheckBox):
                conn = widget.toggled.connect(wrapper)
            elif isinstance(widget, QComboBox):
                conn = widget.currentTextChanged.connect(wrapper)
            elif isinstance(widget, QSlider):
                conn = widget.valueChanged.connect(wrapper)
            elif isinstance(widget, QTabWidget):
                conn = widget.currentChanged.connect(wrapper)
            
        if conn is not None:
            self.event_connections[(node_id, event)] = {"conn": conn, "wrapper": wrapper, "state": state}

    def unbind_event(
        self,
        node_id: str,
        event: str
    ) -> None:
        data = self.event_connections.pop((node_id, event), None)
        if data is not None:
            conn = data["conn"]
            widget = self.registry.get(node_id)
            if widget is not None:
                try:
                    from PySide6.QtWidgets import QLineEdit, QCheckBox, QComboBox, QSlider, QTabWidget
                    if event == "on_click" and hasattr(widget, "clicked"):
                        widget.clicked.disconnect(conn)
                    elif event == "on_change":
                        if isinstance(widget, QLineEdit):
                            widget.textChanged.disconnect(conn)
                        elif isinstance(widget, QCheckBox):
                            widget.toggled.disconnect(conn)
                        elif isinstance(widget, QComboBox):
                            widget.currentTextChanged.disconnect(conn)
                        elif isinstance(widget, QSlider):
                            widget.valueChanged.disconnect(conn)
                        elif isinstance(widget, QTabWidget):
                            widget.currentChanged.disconnect(conn)
                except Exception:
                    pass

    @Slot()
    def _apply_patches(self) -> None:
        patches = self._pending_patches
        self._pending_patches = []
        for patch in patches:
            if isinstance(patch, CreateNode):
                self.create(patch.node_id, patch.type, patch.props, patch.parent_id)
            elif isinstance(patch, UpdateProps):
                self.update(patch.node_id, patch.changed, patch.removed)
            elif isinstance(patch, DestroyNode):
                self.destroy(patch.node_id)
            elif isinstance(patch, SetChildren):
                self.set_children(patch.parent_id, patch.child_ids)
            elif isinstance(patch, MoveNode):
                self.move(patch.node_id, patch.new_parent_id)

    def commit(self, patches: list[Patch]) -> None:
        if self.logger:
            for patch in patches:
                self.logger.commit(patch)
        self._pending_patches.extend(patches)
        QMetaObject.invokeMethod(self, "_apply_patches", Qt.ConnectionType.QueuedConnection)

__all__ = ["QtRenderer"]
