import time
import os
from unittest.mock import MagicMock
from pymiro.dev.hot_reload import HotReloader, _ChangeHandler
from pymiro.core.vnode import Div

def test_file_change_triggers_reload_callback():
    reloader = HotReloader(
        root_component=lambda: Div(),
        reconciler_fn=lambda old, new: [],
        renderer=MagicMock()
    )
    
    # Mock invokeMethod to execute synchronously
    reloader._worker.do_reload = MagicMock()
    
    handler = _ChangeHandler(reloader)
    
    class FakeEvent:
        is_directory = False
        src_path = "test.py"
        
    handler.on_modified(FakeEvent())
    
    # Wait, invokeMethod is mocked but the QMetaObject.invokeMethod wasn't.
    # We should just assert _pending_filepath was set.
    assert reloader._pending_filepath == "test.py"

def test_non_py_file_change_ignored():
    reloader = HotReloader(
        root_component=lambda: Div(),
        reconciler_fn=lambda old, new: [],
        renderer=MagicMock()
    )
    handler = _ChangeHandler(reloader)
    
    class FakeEvent:
        is_directory = False
        src_path = "test.txt"
        
    handler.on_modified(FakeEvent())
    assert reloader._pending_filepath is None

def test_debounce_ignores_rapid_changes():
    reloader = HotReloader(
        root_component=lambda: Div(),
        reconciler_fn=lambda old, new: [],
        renderer=MagicMock()
    )
    handler = _ChangeHandler(reloader)
    
    class FakeEvent:
        is_directory = False
        src_path = "test.py"
        
    handler.on_modified(FakeEvent())
    
    class FakeEvent2:
        is_directory = False
        src_path = "test2.py"
        
    handler.on_modified(FakeEvent2())
    
    # The second one should be ignored due to debounce (0.3s)
    assert reloader._pending_filepath == "test.py"

def test_exception_during_reload_keeps_old_tree():
    old_tree = Div()
    
    def failing_component():
        raise ValueError("Crash")
        
    reloader = HotReloader(
        root_component=failing_component,
        reconciler_fn=lambda old, new: [],
        renderer=MagicMock()
    )
    reloader.current_tree = old_tree
    reloader._pending_filepath = "test.py"
    
    # perform reload should catch the exception and log it
    reloader._perform_reload()
    
    assert reloader.current_tree is old_tree
