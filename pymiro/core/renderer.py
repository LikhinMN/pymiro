"""
Renderer protocol for pymiro.
"""

from typing import Any, Protocol


class Renderer(Protocol):
    def create(
        self, node_id: str, type: str, props: dict[str, Any], parent_id: str | None
    ) -> None: ...

    def update(
        self, node_id: str, changed: dict[str, Any], removed: list[str]
    ) -> None: ...

    def destroy(self, node_id: str) -> None: ...

    def set_children(self, parent_id: str, child_ids: list[str]) -> None: ...

    def move(self, node_id: str, new_parent_id: str) -> None: ...

    def bind_event(self, node_id: str, event: str, handler: Any) -> None: ...

    def unbind_event(self, node_id: str, event: str) -> None: ...

    def commit(self, patches: list[Any]) -> None: ...


__all__ = ["Renderer"]
