# ============================================================
# File: ui/assets/constants.py
# ============================================================

"""
War Chess
UI-2.A - Asset Pipeline

Shared constants used by the entire asset system.

This module intentionally contains NO loading logic.
It only defines:

    • Asset directories
    • Supported formats
    • Cache identifiers
    • Sprite defaults
    • Theme configuration

Every other asset module imports from here.
"""

from pathlib import Path

# ------------------------------------------------------------
# Project Root
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ------------------------------------------------------------
# Asset Directories
# ------------------------------------------------------------

ASSETS_DIR = PROJECT_ROOT / "Assets"

GENERATED_ASSETS_DIR = ASSETS_DIR / "Generated_assets"

UI_ASSETS_DIR = GENERATED_ASSETS_DIR / "UI"

BACKGROUND_ASSETS_DIR = GENERATED_ASSETS_DIR / "Backgrounds"

BUTTON_ASSETS_DIR = GENERATED_ASSETS_DIR / "Buttons"

FRAME_ASSETS_DIR = GENERATED_ASSETS_DIR / "Frames"

ICON_ASSETS_DIR = GENERATED_ASSETS_DIR / "Icons"

PARTICLE_ASSETS_DIR = GENERATED_ASSETS_DIR / "Particles"

CHESS_ASSETS_DIR = GENERATED_ASSETS_DIR / "Chess"

EFFECT_ASSETS_DIR = GENERATED_ASSETS_DIR / "Effects"

FONT_ASSETS_DIR = GENERATED_ASSETS_DIR / "Fonts"

# ------------------------------------------------------------
# Supported Image Formats
# ------------------------------------------------------------

SUPPORTED_IMAGE_FORMATS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
)

# ------------------------------------------------------------
# Theme Support
# ------------------------------------------------------------

DEFAULT_THEME = "default"

AVAILABLE_THEMES = (
    "default",
)

# ------------------------------------------------------------
# Texture Cache Keys
# ------------------------------------------------------------

TEXTURE_CACHE = "texture"

SCALED_TEXTURE_CACHE = "scaled_texture"

SPRITESHEET_CACHE = "spritesheet"

ANIMATION_CACHE = "animation"

BUTTON_CACHE = "button"

CHESS_CACHE = "chess"

ICON_CACHE = "icon"

FONT_CACHE = "font"

# ------------------------------------------------------------
# Sprite Defaults
# ------------------------------------------------------------

DEFAULT_SCALE = 1.0

DEFAULT_ROTATION = 0

DEFAULT_ALPHA = 255

DEFAULT_SMOOTH_SCALE = True

# ------------------------------------------------------------
# Sprite Sheet Defaults
# ------------------------------------------------------------

DEFAULT_MARGIN = 0

DEFAULT_SPACING = 0

# ------------------------------------------------------------
# Animation Defaults
# ------------------------------------------------------------

DEFAULT_FPS = 12

DEFAULT_LOOP = True

# ------------------------------------------------------------
# Texture Filtering
# ------------------------------------------------------------

USE_SMOOTH_SCALING = True

# ------------------------------------------------------------
# Debug
# ------------------------------------------------------------

ENABLE_ASSET_LOGGING = True

LOG_MISSING_ASSETS = True

# ------------------------------------------------------------
# Runtime Limits
# ------------------------------------------------------------

MAX_TEXTURE_CACHE_SIZE = 2048

MAX_ANIMATION_CACHE_SIZE = 512

MAX_SPRITESHEET_CACHE_SIZE = 256

# ------------------------------------------------------------
# Placeholder Asset Names
# ------------------------------------------------------------

MISSING_TEXTURE_NAME = "__missing_texture__"

MISSING_ANIMATION_NAME = "__missing_animation__"

# ------------------------------------------------------------
# UI Naming Convention
# ------------------------------------------------------------

BUTTON_IDLE = "idle"

BUTTON_HOVER = "hover"

BUTTON_PRESSED = "pressed"

BUTTON_DISABLED = "disabled"

# ------------------------------------------------------------
# Chess Piece Names
# ------------------------------------------------------------

WHITE = "white"

BLACK = "black"

KING = "king"

QUEEN = "queen"

ROOK = "rook"

BISHOP = "bishop"

KNIGHT = "knight"

PAWN = "pawn"

PIECE_NAMES = (
    KING,
    QUEEN,
    ROOK,
    BISHOP,
    KNIGHT,
    PAWN,
)

PIECE_COLORS = (
    WHITE,
    BLACK,
)