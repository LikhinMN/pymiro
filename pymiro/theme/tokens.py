"""
Design tokens for pymiro.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class ColorTokens:
    # Base
    background: str
    surface: str
    border: str

    # Text
    text_primary: str
    text_secondary: str
    text_disabled: str

    # Brand
    primary: str
    primary_hover: str
    primary_text: str

    # Semantic
    success: str
    warning: str
    error: str
    info: str

    # Semantic text (on semantic backgrounds)
    success_text: str
    warning_text: str
    error_text: str
    info_text: str

@dataclass(frozen=True)
class SpacingTokens:
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48

@dataclass(frozen=True)
class TypographyTokens:
    font_family: str = "Inter, system-ui, sans-serif"
    font_mono: str = "JetBrains Mono, monospace"
    size_xs: int = 11
    size_sm: int = 13
    size_md: int = 14
    size_lg: int = 16
    size_xl: int = 18
    size_2xl: int = 24
    size_3xl: int = 32
    weight_normal: int = 400
    weight_medium: int = 500
    weight_bold: int = 700
    line_height: float = 1.6

@dataclass(frozen=True)
class RadiusTokens:
    sm: int = 4
    md: int = 6
    lg: int = 8
    xl: int = 12
    full: int = 9999

@dataclass(frozen=True)
class ShadowTokens:
    sm: str = "0 1px 2px rgba(0,0,0,0.05)"
    md: str = "0 2px 8px rgba(0,0,0,0.1)"
    lg: str = "0 4px 16px rgba(0,0,0,0.15)"
