"""
Hot Reloader for pymiro.
"""

import importlib
import os
import sys
import time
import traceback
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QMetaObject, QObject, Qt, Slot
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from pymiro.dev.logger import DevLogger


class _ReloaderWorker(QObject):
    def __init__(self, reloader: "HotReloader") -> None:
        super().__init__()
        self.reloader = reloader

    @Slot()
    def do_reload(self) -> None:
        self.reloader._perform_reload()


class _ChangeHandler(FileSystemEventHandler):
    def __init__(self, reloader: "HotReloader") -> None:
        super().__init__()
        self.reloader = reloader

    def on_modified(self, event: Any) -> None:
        if not event.is_directory and event.src_path.endswith(".py"):
            self.reloader._trigger_reload(event.src_path)


class HotReloader:
    def __init__(
        self,
        root_component: Callable[[], Any],
        reconciler_fn: Callable[[Any, Any], list[Any]],
        renderer: Any,
        watch_dir: str = ".",
        logger: DevLogger | None = None,
    ) -> None:
        self.root_component = root_component
        self.reconciler_fn = reconciler_fn
        self.renderer = renderer
        self.watch_dir = watch_dir
        self.logger = logger

        self.current_tree: Any = None

        self._observer = Observer()
        self._handler = _ChangeHandler(self)
        self._worker = _ReloaderWorker(self)

        self._last_reload_time = 0.0
        self._pending_filepath: str | None = None

    def start(self) -> None:
        self._observer.schedule(self._handler, self.watch_dir, recursive=True)
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()

    def _trigger_reload(self, filepath: str) -> None:
        now = time.time()
        if now - self._last_reload_time < 0.3:
            return
        self._last_reload_time = now
        self._pending_filepath = filepath

        QMetaObject.invokeMethod(
            self._worker, "do_reload", Qt.ConnectionType.QueuedConnection
        )

    def _perform_reload(self) -> None:
        filepath = self._pending_filepath
        if not filepath:
            return

        try:
            # 1. importlib.reload() the changed module
            changed_module = None
            abs_filepath = os.path.abspath(filepath)

            for mod in list(sys.modules.values()):
                if hasattr(mod, "__file__") and mod.__file__:
                    if os.path.abspath(mod.__file__) == abs_filepath:
                        changed_module = mod
                        break

            if changed_module:
                importlib.reload(changed_module)

            # also reload the module containing the root component, just in case
            root_mod = sys.modules.get(self.root_component.__module__)
            if root_mod and root_mod is not changed_module:
                importlib.reload(root_mod)

            # Update root_component reference
            if root_mod:
                new_comp = getattr(root_mod, self.root_component.__name__, None)
                if new_comp is not None:
                    self.root_component = new_comp

            # 2. Re-call root_component()
            new_tree = self.root_component()

            # 3. reconcile
            patches = self.reconciler_fn(self.current_tree, new_tree)

            # 4. commit
            if patches:
                self.renderer.commit(patches)

            # 5. current_tree = new_tree
            self.current_tree = new_tree

            # 6. log
            if self.logger:
                self.logger.reload(os.path.basename(filepath))

        except Exception as e:
            if self.logger:
                self.logger.error(f"Reload error: {e}")
            else:
                traceback.print_exc()


__all__ = ["HotReloader"]
