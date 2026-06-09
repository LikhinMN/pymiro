from dataclasses import dataclass

from pymiro.theme.tokens import (
    ColorTokens,
    RadiusTokens,
    ShadowTokens,
    SpacingTokens,
    TypographyTokens,
)


@dataclass(frozen=True)
class Theme:
    name: str
    colors: ColorTokens
    spacing: SpacingTokens
    typography: TypographyTokens
    radius: RadiusTokens
    shadow: ShadowTokens

    def to_qss(self) -> str:
        c = self.colors
        s = self.spacing
        t = self.typography
        r = self.radius

        qss = f"""
        /* Global Defaults */
        QWidget {{
            background-color: {c.background};
            color: {c.text_primary};
            font-family: {t.font_family};
            font-size: {t.size_md}px;
        }}

        QLabel {{
            background-color: transparent;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {c.surface};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: {r.md}px;
            padding: {s.sm}px {s.md}px;
        }}
        QPushButton:hover {{
            background-color: {c.border};
        }}
        QPushButton:disabled {{
            background-color: {c.surface};
            color: {c.text_disabled};
            border-color: {c.border};
        }}

        /* Button Variants */
        QPushButton[variant="primary"] {{
            background-color: {c.primary};
            color: {c.primary_text};
            border: 1px solid {c.primary};
        }}
        QPushButton[variant="primary"]:hover {{
            background-color: {c.primary_hover};
        }}

        QPushButton[variant="danger"] {{
            background-color: {c.error};
            color: {c.error_text};
            border: 1px solid {c.error};
        }}
        QPushButton[variant="danger"]:hover {{
            background-color: {c.error}; /* Maybe darker in real theme, but we use error for now */
        }}

        QPushButton[variant="ghost"] {{
            background-color: transparent;
            border: none;
        }}
        QPushButton[variant="ghost"]:hover {{
            background-color: {c.surface};
        }}

        /* Inputs */
        QLineEdit, QComboBox {{
            background-color: {c.background};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: {r.md}px;
            padding: {s.sm}px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {c.primary};
        }}
        QLineEdit:disabled, QComboBox:disabled {{
            background-color: {c.surface};
            color: {c.text_disabled};
        }}

        /* Checkbox */
        QCheckBox {{
            color: {c.text_primary};
        }}
        QCheckBox:disabled {{
            color: {c.text_disabled};
        }}

        /* Slider */
        QSlider::groove:horizontal {{
            border: 1px solid {c.border};
            height: {s.sm}px;
            background: {c.surface};
            border-radius: {r.sm}px;
        }}
        QSlider::handle:horizontal {{
            background: {c.primary};
            border: 1px solid {c.primary};
            width: {s.md}px;
            margin: -4px 0;
            border-radius: {r.md}px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {c.primary_hover};
        }}

        /* ProgressBar */
        QProgressBar {{
            border: 1px solid {c.border};
            border-radius: {r.md}px;
            text-align: center;
            color: {c.text_primary};
            background-color: {c.surface};
        }}
        QProgressBar::chunk {{
            background-color: {c.primary};
            border-radius: {r.md}px;
        }}

        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {c.border};
            border-radius: {r.md}px;
        }}
        QTabBar::tab {{
            background: {c.surface};
            border: 1px solid {c.border};
            padding: {s.sm}px {s.md}px;
            color: {c.text_secondary};
            border-top-left-radius: {r.md}px;
            border-top-right-radius: {r.md}px;
        }}
        QTabBar::tab:selected {{
            background: {c.background};
            color: {c.primary};
            border-bottom-color: {c.background};
        }}
        QTabBar::tab:hover:!selected {{
            background: {c.border};
            color: {c.text_primary};
        }}
        """
        return qss


__all__ = ["Theme"]
