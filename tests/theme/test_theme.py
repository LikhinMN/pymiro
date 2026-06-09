from pymiro.theme.presets import DEFAULT_THEME, DARK_THEME

def test_theme_to_qss_returns_non_empty_string():
    qss = DEFAULT_THEME.to_qss()
    assert len(qss) > 0
    assert isinstance(qss, str)

def test_theme_to_qss_contains_button_rules():
    qss = DEFAULT_THEME.to_qss()
    assert "QPushButton {" in qss
    assert 'QPushButton[variant="primary"] {' in qss
    assert 'QPushButton[variant="danger"] {' in qss

def test_theme_to_qss_contains_hover_rules():
    qss = DEFAULT_THEME.to_qss()
    assert ":hover {" in qss

def test_theme_to_qss_contains_disabled_rules():
    qss = DEFAULT_THEME.to_qss()
    assert ":disabled {" in qss

def test_dark_theme_differs_from_light_theme():
    # Colors should differ
    assert DEFAULT_THEME.colors.background != DARK_THEME.colors.background
    
    # QSS should differ
    assert DEFAULT_THEME.to_qss() != DARK_THEME.to_qss()
