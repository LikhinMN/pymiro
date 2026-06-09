"""
Dark theme preset.
"""

from pymiro.theme.theme import Theme
from pymiro.theme.tokens import (
    ColorTokens,
    RadiusTokens,
    ShadowTokens,
    SpacingTokens,
    TypographyTokens,
)

DARK_THEME = Theme(
    name="dark",
    colors=ColorTokens(
        background="#0f0f1a",
        surface="#1a1a2e",
        border="#2d2d44",
        text_primary="#e8e8f0",
        text_secondary="#9898b0",
        text_disabled="#5a5a70",
        primary="#4361ee",
        primary_hover="#5a7bff",
        primary_text="#ffffff",
        success="#52b788",
        warning="#f4a261",
        error="#e63946",
        info="#4895ef",
        success_text="#ffffff",
        warning_text="#ffffff",
        error_text="#ffffff",
        info_text="#ffffff",
    ),
    spacing=SpacingTokens(),
    typography=TypographyTokens(),
    radius=RadiusTokens(),
    shadow=ShadowTokens(),
)
