"""
App entry point for pymiro.
"""
import sys
import asyncio
from typing import Callable

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
import qasync # type: ignore

from pymiro.core.vnode import VNode
from pymiro.core.reconciler import reconcile
from pymiro.backends.qt.renderer import QtRenderer
from pymiro.core.signals import effect

class App:
    def __init__(self, title: str = "pymiro", width: int = 800, height: int = 600) -> None:
        self.title = title
        self.width = width
        self.height = height
        self.renderer: QtRenderer | None = None
        self.current_tree: VNode | None = None

    def run(self, component: Callable[[], VNode]) -> None:
        # 1. create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        # 2. create main QMainWindow
        main_window = QMainWindow()
        main_window.setWindowTitle(self.title)
        main_window.resize(self.width, self.height)
        
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        main_window.setCentralWidget(central_widget)
        
        # 3. setup qasync event loop
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # 4. setup renderer
        self.renderer = QtRenderer(root_widget=central_widget)
        
        is_render_pending = False
        def render_cycle() -> None:
            nonlocal is_render_pending
            is_render_pending = False
            new_tree = component()
            patches = reconcile(self.current_tree, new_tree)
            if patches and self.renderer is not None:
                self.renderer.commit(patches)
            self.current_tree = new_tree

        def schedule_render() -> None:
            nonlocal is_render_pending
            if not is_render_pending:
                is_render_pending = True
                loop.call_soon_threadsafe(render_cycle)

        # initial render
        self._root_dispose = effect(schedule_render)
        
        # Cleanup on exit
        if hasattr(app, "aboutToQuit"):
            app.aboutToQuit.connect(self._root_dispose)
        
        main_window.show()
        
        # 6. start event loop
        with loop:
            loop.run_forever()

__all__ = ["App"]
