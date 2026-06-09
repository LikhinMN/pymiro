import pytest
import asyncio
from pymiro.core.component import component, use_signal, ComponentError
from pymiro.core.vnode import VNode, Div, Text

def test_component_returning_none():
    @component
    def MaybeEmpty():
        show = use_signal(True)
        return Div() if show() else None
        
    # returning None should raise ComponentError
    # wait, when show is True, it returns Div(). 
    # Let's mock the component to just return None directly for the test, 
    # or toggle it.
    @component
    def ReturnsNone():
        return None
        
    with pytest.raises(ComponentError):
        ReturnsNone()

def test_use_signal_called_after_component_body():
    @component
    def BadComponent():
        return Div()
        
    BadComponent()
    
    with pytest.raises(ComponentError):
        use_signal(0)

def test_deeply_nested_components():
    def make_nested(depth):
        if depth == 0:
            return Text("leaf")
        return Div(make_nested(depth - 1))

    @component
    def Deep():
        return make_nested(50)

    tree = Deep()
    assert tree is not None

def test_component_called_concurrently():
    @component
    def Concurrent():
        s = use_signal(0)
        return Text(str(s()))

    async def run():
        results = await asyncio.gather(
            asyncio.to_thread(Concurrent),
            asyncio.to_thread(Concurrent),
            asyncio.to_thread(Concurrent),
        )
        assert all(r.children[0] == "0" for r in results)

    asyncio.run(run())

