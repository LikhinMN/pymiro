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
    def __init__(self, root_widget: QWidget | None = None) -> None:
        super().__init__()
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
                    
        for cid in child_ids:
            child = self.registry.get(cid)
            if child is not None:
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
            
        self.unbind_event(node_id, event)
        
        conn = None
        if event == "on_click" and hasattr(widget, "clicked"):
            conn = widget.clicked.connect(handler)
        elif event == "on_change" and hasattr(widget, "textChanged"):
            conn = widget.textChanged.connect(handler)
            
        if conn is not None:
            self.event_connections[(node_id, event)] = conn

    def unbind_event(
        self,
        node_id: str,
        event: str
    ) -> None:
        conn = self.event_connections.pop((node_id, event), None)
        if conn is not None:
            widget = self.registry.get(node_id)
            if widget is not None:
                if event == "on_click" and hasattr(widget, "clicked"):
                    widget.clicked.disconnect(conn)
                elif event == "on_change" and hasattr(widget, "textChanged"):
                    widget.textChanged.disconnect(conn)

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
        self._pending_patches.extend(patches)
        QMetaObject.invokeMethod(self, "_apply_patches", Qt.ConnectionType.QueuedConnection)

__all__ = ["QtRenderer"]
