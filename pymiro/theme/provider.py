"""
Theme provider for pymiro.
"""
from typing import Callable, Any
from PySide6.QtWidgets import QApplication

from pymiro.theme.theme import Theme
from pymiro.theme.presets.default import DEFAULT_THEME
from pymiro.core.signals import signal

# Global theme signal
_theme_signal = signal(DEFAULT_THEME)

class ThemeProvider:
    _listeners: list[Callable[[Theme], Any]] = []

    @classmethod
    def set(cls, theme: Theme) -> None:
        _theme_signal.set(theme)
        
        # Apply to QApplication if it exists
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(theme.to_qss())
            
        # Notify manual subscribers
        for listener in list(cls._listeners):
            listener(theme)

    @classmethod
    def get(cls) -> Theme:
        return _theme_signal.peek()

    @classmethod
    def subscribe(cls, callback: Callable[[Theme], Any]) -> Callable[[], None]:
        cls._listeners.append(callback)
        
        def dispose() -> None:
            if callback in cls._listeners:
                cls._listeners.remove(callback)
        return dispose

def use_theme() -> Theme:
    """Hook to get the current theme and trigger re-renders on change."""
    return _theme_signal()

__all__ = ["ThemeProvider", "use_theme"]
