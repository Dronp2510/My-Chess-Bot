"""
theme.py
========

Global UI theme definitions for War Chess.

This module intentionally contains NO pygame code.

It only defines immutable configuration objects describing
the visual identity of the game.

Everything in the UI should reference the global `theme`
instance instead of hardcoding colors, spacing or sizes.
"""

from __future__ import annotations

from dataclasses import dataclass


# ============================================================
# Colors
# ============================================================

Color = tuple[int, int, int]


@dataclass(frozen=True)
class ColorPalette:
    """
    Semantic UI color palette.

    These names describe PURPOSE rather than RGB values.
    """

    # --------------------------------------------------------
    # Backgrounds
    # --------------------------------------------------------

    background: Color
    background_secondary: Color

    surface: Color
    panel: Color
    panel_dark: Color

    border: Color

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    text_primary: Color
    text_secondary: Color
    text_disabled: Color

    # --------------------------------------------------------
    # Accent Colors
    # --------------------------------------------------------

    accent_gold: Color
    accent_purple: Color
    accent_blue: Color

    # --------------------------------------------------------
    # Status Colors
    # --------------------------------------------------------

    success: Color
    warning: Color
    error: Color

    # --------------------------------------------------------
    # Misc
    # --------------------------------------------------------

    shadow: Color

    transparent: Color = (0, 0, 0)


# ============================================================
# Typography
# ============================================================


@dataclass(frozen=True)
class Typography:
    """
    Font size definitions.

    NOTE:
        This stores ONLY sizes.

        pygame.font.Font objects belong inside AssetManager.
    """

    font_name: str = "Cinzel"

    title_size: int = 56

    heading_size: int = 36

    subheading_size: int = 28

    body_size: int = 22

    caption_size: int = 18

    small_size: int = 15


# ============================================================
# Spacing
# ============================================================


@dataclass(frozen=True)
class Spacing:
    """
    Standard spacing values.

    Prevents magic numbers throughout the UI.
    """

    xs: int = 4

    sm: int = 8

    md: int = 16

    lg: int = 24

    xl: int = 40

    xxl: int = 64


# ============================================================
# Corner Radius
# ============================================================


@dataclass(frozen=True)
class Radius:
    """
    Shared corner radius values.

    Used by buttons, cards, windows and panels.
    """

    none: int = 0

    small: int = 4

    medium: int = 8

    large: int = 14

    xl: int = 22


# ============================================================
# Animation Defaults
# ============================================================


@dataclass(frozen=True)
class AnimationDefaults:
    """
    Standard animation timings.

    All durations are in seconds.
    """

    instant: float = 0.0

    fast: float = 0.12

    normal: float = 0.25

    slow: float = 0.45

    very_slow: float = 0.80

    tooltip_delay: float = 0.45

    hover_scale: float = 1.05

    pressed_scale: float = 0.96

    fade_speed: float = 0.25


# ============================================================
# Shadows
# ============================================================


@dataclass(frozen=True)
class Shadows:
    """
    Shadow configuration.

    Widgets can use these values for consistency.
    """

    offset_x: int = 4

    offset_y: int = 4

    blur_radius: int = 10

    alpha: int = 120


# ============================================================
# Borders
# ============================================================


@dataclass(frozen=True)
class Borders:
    """
    Shared border widths.
    """

    thin: int = 1

    normal: int = 2

    thick: int = 4


# ============================================================
# Layout
# ============================================================


@dataclass(frozen=True)
class Layout:
    """
    Shared layout metrics.

    Future widgets should use these values instead
    of hardcoding padding.
    """

    panel_padding: int = 20

    card_padding: int = 18

    button_padding_x: int = 24

    button_padding_y: int = 12

    tooltip_padding: int = 10

    screen_margin: int = 36


# ============================================================
# UI Scale
# ============================================================


@dataclass(frozen=True)
class UIScaling:
    """
    Default reference resolution.

    Used later by scaling helpers.
    """

    reference_width: int = 1920

    reference_height: int = 1080

    minimum_scale: float = 0.75

    maximum_scale: float = 1.50


# ============================================================
# Theme
# ============================================================


@dataclass(frozen=True)
class Theme:
    """
    Complete UI theme.

    Every widget should reference the global `theme`
    instance instead of hardcoding values.
    """

    colors: ColorPalette

    typography: Typography

    spacing: Spacing

    radius: Radius

    animation: AnimationDefaults

    shadows: Shadows

    borders: Borders

    layout: Layout

    scaling: UIScaling


# ============================================================
# Scaling Helpers
# ============================================================


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value between a minimum and maximum."""

    return max(minimum, min(value, maximum))


def calculate_scale(
    window_width: int,
    window_height: int,
    scaling: UIScaling,
) -> float:
    """
    Calculate a DPI-independent UI scale.

    The returned value is clamped so the UI never
    becomes unusably tiny or excessively large.
    """

    width_scale = window_width / scaling.reference_width
    height_scale = window_height / scaling.reference_height

    scale = min(width_scale, height_scale)

    return clamp(
        scale,
        scaling.minimum_scale,
        scaling.maximum_scale,
    )


# ============================================================
# Default Dark Fantasy Theme
# ============================================================

_dark_colors = ColorPalette(

    # --------------------------------------------------------
    # Backgrounds
    # --------------------------------------------------------

    background=(13, 13, 18),

    background_secondary=(20, 20, 28),

    surface=(32, 31, 38),

    panel=(42, 40, 47),

    panel_dark=(24, 23, 29),

    border=(116, 92, 47),

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    text_primary=(236, 228, 210),

    text_secondary=(178, 171, 154),

    text_disabled=(118, 118, 118),

    # --------------------------------------------------------
    # Accents
    # --------------------------------------------------------

    accent_gold=(208, 168, 74),

    accent_purple=(118, 62, 174),

    accent_blue=(92, 135, 204),

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    success=(90, 170, 90),

    warning=(212, 173, 56),

    error=(176, 54, 54),

    # --------------------------------------------------------
    # Misc
    # --------------------------------------------------------

    shadow=(0, 0, 0),
)


# ============================================================
# Global Theme
# ============================================================

theme = Theme(

    colors=_dark_colors,

    typography=Typography(),

    spacing=Spacing(),

    radius=Radius(),

    animation=AnimationDefaults(),

    shadows=Shadows(),

    borders=Borders(),

    layout=Layout(),

    scaling=UIScaling(),
)


# ============================================================
# Convenience Functions
# ============================================================


def ui_scale(
    window_size: tuple[int, int],
) -> float:
    """
    Returns the UI scale factor for the current window.
    """

    return calculate_scale(
        window_size[0],
        window_size[1],
        theme.scaling,
    )


def scaled(
    value: float,
    scale: float,
) -> int:
    """
    Scale a UI value and round to an integer.

    Example
    -------
        padding = scaled(
            theme.spacing.lg,
            ui_scale(window.get_size())
        )
    """

    return round(value * scale)


def scaled_spacing(
    value: int,
    window_size: tuple[int, int],
) -> int:
    """
    Scale a spacing value directly from a window size.
    """

    return scaled(
        value,
        ui_scale(window_size),
    )


def scaled_font_size(
    size: int,
    window_size: tuple[int, int],
) -> int:
    """
    Scale a font size while ensuring it never
    becomes unreadably small.
    """

    return max(
        10,
        scaled(size, ui_scale(window_size)),
    )


__all__ = [
    "Theme",
    "ColorPalette",
    "Typography",
    "Spacing",
    "Radius",
    "AnimationDefaults",
    "Shadows",
    "Borders",
    "Layout",
    "UIScaling",
    "theme",
    "ui_scale",
    "scaled",
    "scaled_spacing",
    "scaled_font_size",
]