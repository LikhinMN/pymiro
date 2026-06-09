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
from pymiro.dev import DevLogger, install_error_handler, HotReloader
from pymiro.theme.provider import ThemeProvider
from pymiro.theme.theme import Theme
from pymiro.theme.presets import DEFAULT_THEME, DARK_THEME

class App:
    def __init__(
        self,
        title: str = "pymiro",
        width: int = 800,
        height: int = 600,
        dev: bool = False,
        theme: str | Theme = "default"
    ) -> None:
        self.title = title
        self.width = width
        self.height = height
        self.dev = dev
        self.renderer: QtRenderer | None = None
        self.current_tree: VNode | None = None
        self.logger = DevLogger(enabled=dev)
        self.reloader: HotReloader | None = None
        
        if isinstance(theme, str):
            self.theme = DARK_THEME if theme == "dark" else DEFAULT_THEME
        else:
            self.theme = theme
        
        if self.dev:
            install_error_handler()
            version = sys.version.split(" ")[0]
            print(f"  [pymiro] v0.1.0 | Python {version} | dev mode on")

    def run(self, component: Callable[[], VNode]) -> None:
        # 1. create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            
        ThemeProvider.set(self.theme)
            
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
        self.renderer = QtRenderer(root_widget=central_widget, logger=self.logger)
        
        if self.dev:
            self.logger.mount(component.__name__)
            self.reloader = HotReloader(
                root_component=component,
                reconciler_fn=lambda old, new: reconcile(old, new, logger=self.logger),
                renderer=self.renderer,
                watch_dir=".",
                logger=self.logger
            )
        
        is_render_pending = False
        def render_cycle() -> None:
            nonlocal is_render_pending
            is_render_pending = False
            new_tree = component()
            patches = reconcile(self.current_tree, new_tree, logger=self.logger)
            if patches and self.renderer is not None:
                self.renderer.commit(patches)
            self.current_tree = new_tree
            if self.reloader:
                self.reloader.current_tree = new_tree

        def schedule_render() -> None:
            nonlocal is_render_pending
            if not is_render_pending:
                is_render_pending = True
                loop.call_soon_threadsafe(render_cycle)

        # initial render
        self._root_dispose = effect(schedule_render)
        
        if self.reloader:
            self.reloader.start()
        
        # Cleanup on exit
        if hasattr(app, "aboutToQuit"):
            app.aboutToQuit.connect(self._root_dispose)
            if self.reloader:
                app.aboutToQuit.connect(self.reloader.stop)
        
        main_window.show()
        
        # 6. start event loop
        with loop:
            loop.run_forever()

__all__ = ["App"]
