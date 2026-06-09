"""
Default light theme preset.
"""

from pymiro.theme.theme import Theme
from pymiro.theme.tokens import (
    ColorTokens,
    RadiusTokens,
    ShadowTokens,
    SpacingTokens,
    TypographyTokens,
)

DEFAULT_THEME = Theme(
    name="default",
    colors=ColorTokens(
        background="#ffffff",
        surface="#f8f9fa",
        border="#e9ecef",
        text_primary="#1a1a2e",
        text_secondary="#6c757d",
        text_disabled="#adb5bd",
        primary="#4361ee",
        primary_hover="#3a0ca3",
        primary_text="#ffffff",
        success="#2d6a4f",
        warning="#e76f51",
        error="#d62828",
        info="#4361ee",
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
