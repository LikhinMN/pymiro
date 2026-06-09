import sys
from pymiro.dev.errors import install_error_handler, pymiro_excepthook, _format_error_box
from pymiro.core.component import ComponentError
from pymiro.core.signals import CycleError

def test_install_error_handler():
    original = sys.excepthook
    try:
        install_error_handler()
        assert sys.excepthook is pymiro_excepthook
    finally:
        sys.excepthook = original

def test_component_error_renders_bordered_block(capsys):
    try:
        raise ComponentError("Expected VNode, got <class 'str'>")
    except ComponentError as e:
        pymiro_excepthook(type(e), e, e.__traceback__)
        
    _, err = capsys.readouterr()
    assert "╔══ pymiro error" in err
    assert "ComponentError in test_component_error_renders_bordered_block" in err
    assert "Expected VNode, got <class 'str'>" in err
    assert "Hint: return a VNode from your component" in err
    assert "╚════" in err

def test_cycle_error_renders_with_correct_hint(capsys):
    try:
        raise CycleError("Cycle detected")
    except CycleError as e:
        pymiro_excepthook(type(e), e, e.__traceback__)
        
    _, err = capsys.readouterr()
    assert "╔══ pymiro error" in err
    assert "CycleError in test_cycle_error_renders_with_correct_hint" in err
    assert "Cycle detected" in err
    assert "Hint: a computed value cannot depend on itself" in err

def test_missing_key_warn(capsys):
    try:
        raise ValueError("Missing key in list")
    except ValueError as e:
        # Not a pymiro error explicitly by name, but contains "key" so hint triggers IF it was marked as a pymiro error.
        # But wait, pymiro_excepthook only handles ComponentError, CycleError, or if "pymiro" in str(exc_type).
        # We need to make sure ValueError with "key" is handled? The prompt says: "Missing key warn -> 'add key= props to list children'".
        # In our implementation we check if "key" is in str(exc_value).
        pass

    # Let's test the hint directly
    from pymiro.dev.errors import _get_hint
    hints = _get_hint(ValueError, ValueError("Missing key in children"))
    assert "Hint: add key= props to list children" in hints[0]
