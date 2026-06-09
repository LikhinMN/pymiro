import pytest
import gc
import tracemalloc
import weakref
from pymiro.core.signals import signal, computed, effect

def test_no_memory_leak():
    tracemalloc.start()
    
    # Run gc to ensure a clean slate before snapshot1
    gc.collect()
    snapshot1 = tracemalloc.take_snapshot()

    a = signal(0)
    runs = []
    dispose = effect(lambda: runs.append(a()))

    for i in range(1000):
        a.set(i)

    dispose()
    
    # Need to delete local variables to allow GC to clean them up
    del a
    del dispose
    
    gc.collect()

    snapshot2 = tracemalloc.take_snapshot()
    stats = snapshot2.compare_to(snapshot1, 'lineno')
    # Sum up all the diffs to ensure no leak
    total_diff = sum(stat.size_diff for stat in stats)

    assert total_diff < 1_000_000, f"Memory leak: {total_diff} bytes"

def test_disposed_effect_leaves_no_subscribers():
    a = signal(0)
    dispose = effect(lambda: a())
    dispose()

    assert len(a._subscribers) == 0

def test_computed_chain_garbage_collection():
    a = signal(0)
    b = computed(lambda: a() * 2)
    ref = weakref.ref(b)

    del b
    gc.collect()

    assert ref() is None
