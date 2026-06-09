import pytest
from pymiro.core.signals import signal, computed, effect, batch

def test_diamond_dependency():
    a = signal(1)
    b = computed(lambda: a() * 2)
    c = computed(lambda: a() * 3)
    d = computed(lambda: b() + c())

    effect_runs = []
    effect(lambda: effect_runs.append(d()))

    a.set(2)
    assert len(effect_runs) == 2

def test_glitch_free_guarantee():
    a = signal(0)
    b = computed(lambda: a())
    c = computed(lambda: a() + b())

    seen = []
    effect(lambda: seen.append(c()))
    a.set(1)
    assert seen == [0, 2]

def test_effect_inside_computed():
    with pytest.raises(Exception): # Assuming some exception is raised
        s = signal(0)
        c = computed(lambda: effect(lambda: None))
        c()

def test_rapid_signal_updates_inside_effect():
    a = signal(0)
    results = []

    def runner():
        v = a()
        results.append(v)
        if v < 3:
            a.set(v + 1)

    effect(runner)
    assert results == [0, 1, 2, 3]

def test_computed_no_dependencies():
    c = computed(lambda: 42)
    assert c() == 42

def test_signal_set_to_same_value():
    a = signal(5)
    runs = []
    effect(lambda: runs.append(a()))
    a.set(5)
    assert len(runs) == 1

def test_nested_batch():
    a = signal(0)
    b = signal(0)
    runs = []
    effect(lambda: runs.append((a(), b())))

    with batch():
        a.set(1)
        with batch():
            b.set(2)
            
    assert len(runs) == 2
    assert runs[-1] == (1, 2)
