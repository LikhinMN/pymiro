import pytest
from dataclasses import FrozenInstanceError

from pymiro.theme.tokens import ColorTokens, SpacingTokens, TypographyTokens

def test_color_tokens_is_frozen():
    colors = ColorTokens(
        background="#000",
        surface="#111",
        border="#222",
        text_primary="#fff",
        text_secondary="#aaa",
        text_disabled="#555",
        primary="#blue",
        primary_hover="#darkblue",
        primary_text="#fff",
        success="#green",
        warning="#yellow",
        error="#red",
        info="#cyan",
        success_text="#fff",
        warning_text="#000",
        error_text="#fff",
        info_text="#fff"
    )
    with pytest.raises(FrozenInstanceError):
        colors.background = "#fff" # type: ignore

def test_spacing_tokens_defaults():
    s = SpacingTokens()
    assert s.xs == 4
    assert s.sm == 8
    assert s.md == 16
    assert s.lg == 24
    assert s.xl == 32
    assert s.xxl == 48

def test_typography_tokens_defaults():
    t = TypographyTokens()
    assert t.size_md == 14
    assert t.weight_bold == 700
