import io
import sys
from pymiro.dev.logger import DevLogger

def test_logger_emits_correct_format(capsys):
    logger = DevLogger(enabled=True)
    logger.mount("Counter")
    out, _ = capsys.readouterr()
    assert "[pymiro]" in out
    assert "mount" in out
    assert "Counter" in out
    assert "\033[36m" in out # cyan for mount

def test_logger_signal(capsys):
    logger = DevLogger(enabled=True)
    logger.signal("count", 0, 1)
    out, _ = capsys.readouterr()
    assert "signal" in out
    assert "count: 0 \u2192 1" in out
    assert "\033[33m" in out # yellow

def test_logger_reconcile(capsys):
    logger = DevLogger(enabled=True)
    logger.reconcile(3)
    out, _ = capsys.readouterr()
    assert "reconcile" in out
    assert "3 patches" in out
    assert "\033[34m" in out # blue

def test_logger_commit(capsys):
    logger = DevLogger(enabled=True)
    class FakePatch:
        node_id = "node_3"
    patch = FakePatch()
    logger.commit(patch)
    out, _ = capsys.readouterr()
    assert "commit" in out
    assert "FakePatch node_3" in out
    assert "\033[32m" in out # green

def test_logger_reload(capsys):
    logger = DevLogger(enabled=True)
    logger.reload("counter.py")
    out, _ = capsys.readouterr()
    assert "reload" in out
    assert "counter.py" in out
    assert "\033[35m" in out # magenta

def test_logger_error(capsys):
    logger = DevLogger(enabled=True)
    logger.error("Something went wrong")
    out, _ = capsys.readouterr()
    assert "error" in out
    assert "Something went wrong" in out
    assert "\033[31m" in out # red

def test_logger_silent_when_disabled(capsys):
    logger = DevLogger(enabled=False)
    logger.mount("Counter")
    logger.signal("count", 0, 1)
    out, _ = capsys.readouterr()
    assert out == ""
