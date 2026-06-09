import pytest
from unittest.mock import Mock
import gc

from pymiro.core.signals import signal, computed, effect, batch, CycleError

def test_signal_read_write():
    count = signal(0)
    assert count() == 0
    count.set(1)
    assert count() == 1
    
    # peek
    count.set(2)
    assert count.peek() == 2

def test_computed_auto_tracks_dependencies():
    first = signal("Hello")
    last = signal("World")
    
    full = computed(lambda: f"{first()} {last()}")
    assert full() == "Hello World"
    
    first.set("Hi")
    assert full() == "Hi World"

def test_computed_is_lazy():
    count = signal(1)
    eval_count = 0
    
    def double():
        nonlocal eval_count
        eval_count += 1
        return count() * 2
        
    doubled = computed(double)
    assert eval_count == 0 # Lazy, not evaluated yet
    
    assert doubled() == 2
    assert eval_count == 1
    
    # Reading again without changes should not re-evaluate
    assert doubled() == 2
    assert eval_count == 1
    
    # Changing dependency should mark as dirty, but NOT evaluate
    count.set(2)
    assert eval_count == 1
    
    # Now it evaluates
    assert doubled() == 4
    assert eval_count == 2

def test_effect_runs_immediately():
    count = signal(1)
    runs = 0
    
    def my_effect():
        nonlocal runs
        runs += 1
        count()
        
    effect(my_effect)
    assert runs == 1

def test_effect_reruns_on_dependency_change():
    count = signal(1)
    runs = 0
    
    def my_effect():
        nonlocal runs
        runs += 1
        count()
        
    effect(my_effect)
    assert runs == 1
    
    count.set(2)
    assert runs == 2

def test_effect_disposer_stops_reruns():
    count = signal(1)
    runs = 0
    
    def my_effect():
        nonlocal runs
        runs += 1
        count()
        
    dispose = effect(my_effect)
    assert runs == 1
    
    count.set(2)
    assert runs == 2
    
    dispose()
    count.set(3)
    assert runs == 2 # Should not run again

def test_batch_defers_notifications():
    first = signal("A")
    last = signal("B")
    
    runs = 0
    def my_effect():
        nonlocal runs
        runs += 1
        first()
        last()
        
    effect(my_effect)
    assert runs == 1
    
    with batch():
        first.set("C")
        last.set("D")
        assert runs == 1 # Deferred
        
    assert runs == 2 # Ran exactly once after batch

def test_computed_depending_on_signal_depending_on_signal_chain():
    # signal -> computed -> computed -> effect
    num = signal(1)
    double = computed(lambda: num() * 2)
    quad = computed(lambda: double() * 2)
    
    runs = 0
    def my_effect():
        nonlocal runs
        runs += 1
        quad()
        
    effect(my_effect)
    assert runs == 1
    assert quad() == 4
    
    num.set(2)
    assert runs == 2
    assert quad() == 8

def test_cycle_detection_raises_cycle_error():
    num = signal(1)
    
    # Creating a cycle: c1 reads c2, c2 reads c1
    # Since they are lazy, cycle happens on evaluation
    c1 = computed(lambda: c2())
    c2 = computed(lambda: c1())
    
    with pytest.raises(CycleError, match="Cycle detected"):
        c1()

    # Self cycle
    c3 = computed(lambda: c3())
    with pytest.raises(CycleError, match="Cycle detected"):
        c3()

    # Effect cycle
    runs = 0
    s_effect = signal(1)
    def cyclic_effect():
        nonlocal runs
        runs += 1
        val = s_effect()
        s_effect.set(val + 1)
        
    with pytest.raises(CycleError, match="Cycle detected"):
        effect(cyclic_effect)

def test_signal_peek_does_not_create_subscription():
    num = signal(1)
    runs = 0
    
    def my_effect():
        nonlocal runs
        runs += 1
        # Use peek instead of call
        num.peek()
        
    effect(my_effect)
    assert runs == 1
    
    num.set(2)
    assert runs == 1 # Should not re-run because it wasn't tracked

def test_effect_cleanup_no_memory_leak():
    s = signal(1)
    
    def create_effect():
        def my_effect():
            s()
        return effect(my_effect)
        
    dispose = create_effect()
    
    # The effect is subscribed to s
    # We can inspect the internal state since it's a test
    assert len(s._subscribers) == 1
    
    dispose()
    
    # After dispose, the subscription should be removed
    assert len(s._subscribers) == 0

def test_batch_function_decorator():
    num = signal(1)
    runs = 0
    
    def my_effect():
        nonlocal runs
        runs += 1
        num()
        
    effect(my_effect)
    assert runs == 1
    
    def update():
        num.set(2)
        num.set(3)
        return "done"
        
    res = batch(update)
    assert res == "done"
    assert runs == 2 # Only ran once for the whole update
