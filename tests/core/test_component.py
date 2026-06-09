import pytest
from pymiro.core.component import component, use_signal, use_computed, use_effect, ComponentError
from pymiro.core.vnode import Div, Text, Button

def test_component_wraps_function_correctly():
    @component
    def MyComponent(title: str):
        """A simple component."""
        return Div(Text(title))
        
    assert MyComponent.__name__ == "MyComponent"
    assert MyComponent.__doc__ == "A simple component."
    assert getattr(MyComponent, "__pymiro_component__", False) is True

def test_component_returns_vnode():
    @component
    def Counter():
        return Div()
        
    tree = Counter()
    assert tree.type == "div"

def test_component_raises_error_if_not_vnode():
    @component
    def BadComponent():
        return "Just text"
        
    with pytest.raises(ComponentError, match="must return a VNode"):
        BadComponent()

def test_hooks_raise_error_outside_component():
    with pytest.raises(ComponentError, match="must be called inside a component"):
        use_signal(1)
        
    with pytest.raises(ComponentError, match="must be called inside a component"):
        use_computed(lambda: 1)
        
    with pytest.raises(ComponentError, match="must be called inside a component"):
        use_effect(lambda: None)

def test_hooks_inside_component():
    effect_ran = False
    
    @component
    def CounterHookTest(start: int):
        count = use_signal(start)
        doubled = use_computed(lambda: count() * 2)
        
        def effect_fn():
            nonlocal effect_ran
            count() # subscribe
            effect_ran = True
            
        use_effect(effect_fn)
        
        return Div(Text(f"Count: {count()}, Double: {doubled()}"))
        
    tree = CounterHookTest(5)
    assert tree.type == "div"
    assert tree.children[0].children[0] == "Count: 5, Double: 10"
    assert effect_ran is True

def test_signal_change_produces_correct_new_vnode():
    from pymiro.core.signals import signal
    global_signal = signal(10)
    
    @component
    def TestComp():
        return Div(Text(f"Val: {global_signal()}"))
        
    tree1 = TestComp()
    assert tree1.children[0].children[0] == "Val: 10"
    
    global_signal.set(20)
    tree2 = TestComp()
    assert tree2.children[0].children[0] == "Val: 20"

def test_prompt_example_works():
    @component
    def Counter():
        count = use_signal(0)
        return Div(
            Text(f"Count: {count()}"),
            Button("Increment", on_click=lambda: count.set(count() + 1))
        )

    tree = Counter()
    assert tree.type == "div"
    assert tree.children[0].children[0] == "Count: 0"
    
    # Simulate a click on the button
    on_click = tree.children[1].props["on_click"]
    on_click()
