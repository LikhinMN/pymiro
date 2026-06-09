"""
Reconciler for pymiro VNode trees.
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any, Callable

from pymiro.core.vnode import VNode

@dataclass
class CreateNode:
    node_id: str
    type: str
    props: dict[str, Any]
    parent_id: str | None

@dataclass
class UpdateProps:
    node_id: str
    changed: dict[str, Any]
    removed: list[str]

@dataclass
class DestroyNode:
    node_id: str

@dataclass
class SetChildren:
    parent_id: str
    child_ids: list[str]

@dataclass
class MoveNode:
    node_id: str
    new_parent_id: str

type Patch = CreateNode | UpdateProps | DestroyNode | SetChildren | MoveNode


def get_node_id(parent_id: str | None, index: int, key: str | None) -> str:
    """Generate a deterministic node ID."""
    prefix = parent_id if parent_id else "root"
    if key is not None:
        return f"{prefix}:{key}"
    return f"{prefix}:{index}"


def _diff_children(
    old_children: list[VNode | str], 
    new_children: list[VNode | str], 
    parent_id: str, 
    patches: list[Patch]
) -> None:
    old_vnodes = [c for c in old_children if isinstance(c, VNode)]
    new_vnodes = [c for c in new_children if isinstance(c, VNode)]
    
    use_keys = any(c.key is not None for c in old_vnodes) or any(c.key is not None for c in new_vnodes)
    
    if not use_keys:
        max_len = max(len(old_vnodes), len(new_vnodes))
        child_ids = []
        needs_set_children = len(old_vnodes) != len(new_vnodes)
        
        for i in range(max_len):
            old_c = old_vnodes[i] if i < len(old_vnodes) else None
            new_c = new_vnodes[i] if i < len(new_vnodes) else None
            
            if new_c is not None:
                c_id = _diff_nodes(old_c, new_c, parent_id, i, patches)
                child_ids.append(c_id)
                if old_c is not None and old_c.type != new_c.type:
                    needs_set_children = True
            elif old_c is not None:
                c_id = get_node_id(parent_id, i, None)
                _destroy_tree(old_c, c_id, patches)
                
        if needs_set_children:
            patches.append(SetChildren(parent_id=parent_id, child_ids=child_ids))
            
    else:
        old_map = {}
        for i, c in enumerate(old_vnodes):
            k = c.key if c.key is not None else f"__unkeyed_{i}"
            if k in old_map:
                raise ValueError(f"Duplicate key: {k}")
            old_map[k] = c
            
        new_map = {}
        for i, c in enumerate(new_vnodes):
            k = c.key if c.key is not None else f"__unkeyed_{i}"
            if k in new_map:
                raise ValueError(f"Duplicate key: {k}")
            new_map[k] = c
        
        old_keys = [c.key if c.key is not None else f"__unkeyed_{i}" for i, c in enumerate(old_vnodes)]
        new_keys = [c.key if c.key is not None else f"__unkeyed_{i}" for i, c in enumerate(new_vnodes)]
        
        last_index = 0
        needs_set_children = len(old_vnodes) != len(new_vnodes)
        
        for i, new_c in enumerate(new_vnodes):
            key = new_keys[i]
            node_id = get_node_id(parent_id, i, new_c.key)
            
            if key in old_map:
                old_c = old_map[key]
                _diff_nodes(old_c, new_c, parent_id, i, patches)
                
                if old_c.type != new_c.type:
                    needs_set_children = True
                    
                old_index = old_keys.index(key)
                if old_index < last_index:
                    patches.append(MoveNode(node_id=node_id, new_parent_id=parent_id))
                    needs_set_children = True
                else:
                    last_index = old_index
            else:
                _diff_nodes(None, new_c, parent_id, i, patches)
                needs_set_children = True
                
        for i, old_c in enumerate(old_vnodes):
            key = old_keys[i]
            if key not in new_map:
                c_id = get_node_id(parent_id, i, old_c.key)
                _destroy_tree(old_c, c_id, patches)
                
        old_ids = [get_node_id(parent_id, i, c.key) for i, c in enumerate(old_vnodes)]
        new_ids = [get_node_id(parent_id, i, c.key) for i, c in enumerate(new_vnodes)]
        
        if old_ids != new_ids or needs_set_children:
            patches.append(SetChildren(parent_id=parent_id, child_ids=new_ids))


def _destroy_tree(node: VNode, node_id: str, patches: list[Patch]) -> None:
    for i, child in enumerate(node.children):
        if isinstance(child, VNode):
            c_id = get_node_id(node_id, i, child.key)
            _destroy_tree(child, c_id, patches)
            
    if "__disposers__" in node.props:
        for disp in node.props["__disposers__"]:
            disp()
            
    patches.append(DestroyNode(node_id=node_id))


def _diff_nodes(
    old_node: VNode | None,
    new_node: VNode,
    parent_id: str | None,
    index: int,
    patches: list[Patch]
) -> str:
    node_id = get_node_id(parent_id, index, new_node.key)
    
    if old_node is not None and "__disposers__" in old_node.props:
        # Call disposers from previous render
        for disp in old_node.props["__disposers__"]:
            disp()
            
    if old_node is None:
        props = dict(new_node.props)
        if new_node.children and isinstance(new_node.children[0], str):
            props["children"] = new_node.children
            
        patches.append(CreateNode(
            node_id=node_id,
            type=new_node.type,
            props=props,
            parent_id=parent_id
        ))
        
        child_ids = []
        for i, child in enumerate(new_node.children):
            if isinstance(child, VNode):
                c_id = _diff_nodes(None, child, node_id, i, patches)
                child_ids.append(c_id)
                
        if child_ids:
            patches.append(SetChildren(parent_id=node_id, child_ids=child_ids))
            
        return node_id

    if old_node.type != new_node.type:
        _destroy_tree(old_node, node_id, patches)
        
        props = dict(new_node.props)
        if new_node.children and isinstance(new_node.children[0], str):
            props["children"] = new_node.children
            
        patches.append(CreateNode(
            node_id=node_id,
            type=new_node.type,
            props=props,
            parent_id=parent_id
        ))
        
        child_ids = []
        for i, child in enumerate(new_node.children):
            if isinstance(child, VNode):
                c_id = _diff_nodes(None, child, node_id, i, patches)
                child_ids.append(c_id)
                
        if child_ids:
            patches.append(SetChildren(parent_id=node_id, child_ids=child_ids))
            
        return node_id
        
    changed: dict[str, Any] = {}
    removed: list[str] = []
    
    for k, v in new_node.props.items():
        if k not in old_node.props or old_node.props[k] != v:
            changed[k] = v
            
    for k in old_node.props:
        if k not in new_node.props:
            removed.append(k)

    old_has_str = bool(old_node.children) and isinstance(old_node.children[0], str)
    new_has_str = bool(new_node.children) and isinstance(new_node.children[0], str)
    
    if new_has_str:
        if not old_has_str or old_node.children != new_node.children:
            changed["children"] = new_node.children
    elif old_has_str and not new_has_str:
        removed.append("children")
        
    if changed or removed:
        patches.append(UpdateProps(node_id=node_id, changed=changed, removed=removed))

    if not new_has_str and not old_has_str:
        _diff_children(old_node.children, new_node.children, node_id, patches)

    return node_id


def reconcile(old_tree: VNode | None, new_tree: VNode | None) -> list[Patch]:
    """
    Diff two VNode trees and produce a minimal list of patches to transform old into new.
    """
    patches: list[Patch] = []
    if new_tree is None:
        if old_tree is not None:
            _destroy_tree(old_tree, "root:0", patches)
        return patches
    _diff_nodes(old_tree, new_tree, None, 0, patches)
    return patches


class ReconcilerScheduler:
    """
    Batches multiple scheduled reconcile calls within one event loop tick.
    """
    def __init__(self, on_commit: Callable[[list[Patch]], None]) -> None:
        self.on_commit = on_commit
        self._pending_tasks: list[Callable[[], list[Patch]]] = []

    def schedule(self, fn: Callable[[], list[Patch]]) -> None:
        self._pending_tasks.append(fn)

    async def run_loop(self) -> None:
        while True:
            if self._pending_tasks:
                tasks = self._pending_tasks[:]
                self._pending_tasks.clear()
                
                all_patches: list[Patch] = []
                for task in tasks:
                    all_patches.extend(task())
                
                if all_patches:
                    self.on_commit(all_patches)
            
            await asyncio.sleep(0)

__all__ = [
    "CreateNode", "UpdateProps", "DestroyNode", "SetChildren", "MoveNode",
    "Patch", "reconcile", "ReconcilerScheduler"
]
