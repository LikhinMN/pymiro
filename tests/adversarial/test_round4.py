import pytest
from pymiro.core.component import component
from pymiro.core.vnode import Text
from pymiro.theme.provider import ThemeProvider, use_theme
from pymiro.theme.presets import DEFAULT_THEME, DARK_THEME

def test_theme_switch_mid_render():
    seen_themes = []

    @component
    def ThemeReader():
        theme = use_theme()
        seen_themes.append(theme.name)
        return Text(theme.name)

    ThemeProvider.set(DEFAULT_THEME)
    ThemeReader()
    ThemeProvider.set(DARK_THEME)
    ThemeReader()

    assert seen_themes[0] != seen_themes[1]
    assert "dark" in seen_themes[1].lower()

def test_to_qss_output_validity():
    qss = DEFAULT_THEME.to_qss()
    for widget in ["QWidget", "QPushButton", "QLabel",
                   "QLineEdit", "QComboBox", "QCheckBox",
                   "QSlider", "QProgressBar"]:
        assert widget in qss, f"Missing QSS rule for {widget}"

    import re
    token_colors = set(vars(DEFAULT_THEME.colors).values())
    hex_pattern = re.compile(r'#[0-9a-fA-F]{3,8}')
    found_hex = set(hex_pattern.findall(qss))
    unknown = found_hex - token_colors
    assert not unknown, f"Hardcoded colors in QSS: {unknown}"
