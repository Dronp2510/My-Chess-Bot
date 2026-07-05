# ============================================================
# File: ui/assets/chess_cache.py
# ============================================================

"""
War Chess
UI-2.B Polish-1

Production Chess Piece Cache

Responsibilities
----------------
• Load themed chess pieces
• Automatically trim transparent borders
• Normalize sprite sizes
• Cache processed assets
• Provide per-piece scaling
• Prepare metadata for future renderers

Game code should NEVER load chess textures directly.
Always retrieve them through ChessPieceManager.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from .cache import asset_cache
from .constants import (
    PIECE_COLORS,
    PIECE_NAMES,
)
from .spritesheet import sprite_sheet_loader


# ============================================================
# Asset Metadata
# ============================================================

@dataclass(frozen=True, slots=True)
class ChessPieceAsset:
    color: str
    piece: str
    surface: pygame.Surface
    base_scale: float


# ============================================================
# Chess Piece Manager
# ============================================================

class ChessPieceManager:

    def __init__(self):

        self.theme = "default"

        self.sheet = None

        self.ATLAS_PATH = (
            Path("Assets")
            / "Generated_assets"
            / "Themed_pieces"
            / "Chess_pieces_1.png"
        )

        # ----------------------------------------------------
        # Large capture rectangles
        #
        # These intentionally include surrounding transparent
        # pixels. SpriteSheet trims them automatically.
        # ----------------------------------------------------

        self.PIECE_RECTS = {

            "white": {

                "king":   (20,   25, 190, 455),
                "queen":  (220,  45, 210, 435),
                "rook":   (455,  80, 205, 390),
                "bishop": (690,  60, 205, 405),
                "knight": (930,  45, 255, 435),
                "pawn":   (1215, 135, 185, 345),
            },

            "black": {

                "king":   (20,  535, 190, 455),
                "queen":  (225, 555, 210, 435),
                "rook":   (460, 590, 205, 390),
                "bishop": (690, 570, 205, 405),
                "knight": (930, 555, 255, 435),
                "pawn":   (1215, 645, 185, 345),
            },
        }

        # ----------------------------------------------------
        # Optical scaling
        #
        # The renderer receives visually consistent pieces
        # regardless of the artwork dimensions.
        # ----------------------------------------------------

        self.BASE_SCALE = {

            "king":   1.00,
            "queen":  0.97,
            "rook":   0.91,
            "bishop": 0.95,
            "knight": 0.98,
            "pawn":   0.82,
        }

    # --------------------------------------------------------
    # Internal
    # --------------------------------------------------------

    def _atlas(self):

        if self.sheet is None:
            self.sheet = sprite_sheet_loader.load(
                self.ATLAS_PATH
            )

        return self.sheet

    @staticmethod
    def _validate(
        color: str,
        piece: str,
    ):

        if color not in PIECE_COLORS:
            raise ValueError(
                f"Unknown piece color: {color}"
            )

        if piece not in PIECE_NAMES:
            raise ValueError(
                f"Unknown piece: {piece}"
            )

    # --------------------------------------------------------
    # Loading
    # --------------------------------------------------------

    def load(
        self,
        color: str,
        piece: str,
    ) -> pygame.Surface:

        self._validate(color, piece)

        if asset_cache.has_piece(color, piece):
            return asset_cache.get_piece(
                color,
                piece,
            )

        x, y, w, h = self.PIECE_RECTS[color][piece]

        surface = self._atlas().frame(
            x,
            y,
            w,
            h,
            trim=True,
            padding=6,
        )

        asset_cache.store_piece(
            color,
            piece,
            surface,
        )

        return surface

    # --------------------------------------------------------
    # Bulk preload
    # --------------------------------------------------------

    def preload(self):

        for color in PIECE_COLORS:
            for piece in PIECE_NAMES:
                self.load(color, piece)

    # --------------------------------------------------------
    # Lookup
    # --------------------------------------------------------

    def get(
        self,
        color: str,
        piece: str,
    ) -> pygame.Surface:

        surface = asset_cache.get_piece(
            color,
            piece,
        )

        if surface is None:
            return self.load(
                color,
                piece,
            )

        return surface

    # --------------------------------------------------------
    # Scaling
    # --------------------------------------------------------

    def get_scaled(
        self,
        color: str,
        piece: str,
        size: tuple[int, int],
    ) -> pygame.Surface:

        surface = self.get(
            color,
            piece,
        )

        multiplier = self.BASE_SCALE[piece]

        width = max(
            1,
            int(size[0] * multiplier),
        )

        height = max(
            1,
            int(size[1] * multiplier),
        )

        return pygame.transform.smoothscale(
            surface,
            (
                width,
                height,
            ),
        )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    def get_base_scale(
        self,
        piece: str,
    ) -> float:

        return self.BASE_SCALE[piece]

    # --------------------------------------------------------
    # Theme
    # --------------------------------------------------------

    def set_theme(
        self,
        theme: str,
    ):

        self.theme = theme

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    def clear(self):

        asset_cache.clear_pieces()


# ------------------------------------------------------------
# Global Manager
# ------------------------------------------------------------

chess_piece_manager = ChessPieceManager()