from pymiro.theme.provider import ThemeProvider, use_theme
from pymiro.theme.presets import DEFAULT_THEME, DARK_THEME

def test_theme_provider_get_returns_default():
    # Make sure we start with DEFAULT_THEME
    ThemeProvider.set(DEFAULT_THEME)
    assert ThemeProvider.get() == DEFAULT_THEME

def test_theme_provider_set_updates_theme():
    ThemeProvider.set(DARK_THEME)
    assert ThemeProvider.get() == DARK_THEME
    
    # Cleanup
    ThemeProvider.set(DEFAULT_THEME)

def test_subscribe_fires_on_change():
    called_with = None
    def on_change(theme):
        nonlocal called_with
        called_with = theme
        
    dispose = ThemeProvider.subscribe(on_change)
    
    ThemeProvider.set(DARK_THEME)
    assert called_with == DARK_THEME
    
    dispose()
    ThemeProvider.set(DEFAULT_THEME)

def test_subscribe_disposer_stops_callbacks():
    calls = 0
    def on_change(theme):
        nonlocal calls
        calls += 1
        
    dispose = ThemeProvider.subscribe(on_change)
    
    ThemeProvider.set(DARK_THEME)
    assert calls == 1
    
    dispose()
    
    ThemeProvider.set(DEFAULT_THEME)
    assert calls == 1 # unchanged

def test_use_theme_returns_current_theme():
    # Since use_theme() reads from signal, it can be tested without component context
    # but normally should be inside one.
    ThemeProvider.set(DEFAULT_THEME)
    assert use_theme() == DEFAULT_THEME
    
    ThemeProvider.set(DARK_THEME)
    assert use_theme() == DARK_THEME
    
    # Cleanup
    ThemeProvider.set(DEFAULT_THEME)
