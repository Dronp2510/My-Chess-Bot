# ============================================================
# File: ui/assets/chess_cache.py
# ============================================================

"""
War Chess
UI-2.A - Asset Pipeline

Chess Piece Cache

Responsibilities
----------------
• Load chess piece textures
• Cache loaded pieces
• Validate piece names
• Support themes
• Support future skins
• Provide a clean API for retrieving pieces

Game code should NEVER load chess textures directly.
Always use ChessPieceManager.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from .cache import asset_cache
from .spritesheet import sprite_sheet_loader
from .constants import (
    PIECE_COLORS,
    PIECE_NAMES,
)


# ============================================================
# Chess Piece
# ============================================================

@dataclass(frozen=True, slots=True)
class ChessPieceAsset:
    """
    Represents one chess piece asset.
    """

    color: str
    piece: str
    surface: pygame.Surface


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

        #
        # Rectangle layout inside the atlas.
        #
        # Format:
        # (x, y, width, height)
        #

        self.PIECE_RECTS = {

            "white": {

                "king":   (35, 55, 150, 395),
                "queen":  (250, 80, 150, 370),
                "rook":   (495, 120, 150, 330),
                "bishop": (730, 95, 145, 355),
                "knight": (975, 90, 180, 360),
                "pawn":   (1260, 180, 115, 270),
            },

            "black": {

                "king":   (35, 565, 150, 395),
                "queen":  (255, 590, 150, 370),
                "rook":   (500, 630, 150, 330),
                "bishop": (735, 605, 145, 355),
                "knight": (975, 600, 180, 360),
                "pawn":   (1260, 690, 115, 270),
            },
        }


    def _atlas(self):

        if self.sheet is None:
            self.sheet = sprite_sheet_loader.load(
                self.ATLAS_PATH
            )

        return self.sheet


    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    @staticmethod
    def _validate(
        color: str,
        piece: str,
    ) -> None:

        if color not in PIECE_COLORS:
            raise ValueError(
                f"Unknown piece color: {color}"
            )

        if piece not in PIECE_NAMES:
            raise ValueError(
                f"Unknown chess piece: {piece}"
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

        sheet = self._atlas()

        x, y, w, h = self.PIECE_RECTS[color][piece]

        surface = sheet.frame(
            x,
            y,
            w,
            h,
        )

        asset_cache.store_piece(
            color,
            piece,
            surface,
        )

        return surface

    # --------------------------------------------------------
    # Bulk Loading
    # --------------------------------------------------------

    def preload(self) -> None:
        """
        Load every chess piece into memory.
        """

        for color in PIECE_COLORS:

            for piece in PIECE_NAMES:

                self.load(
                    color,
                    piece,
                )

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

        return pygame.transform.smoothscale(
            surface,
            size,
        )

    # --------------------------------------------------------
    # Theme
    # --------------------------------------------------------

    def set_theme(
        self,
        theme: str,
    ) -> None:

        self.theme = theme

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    def clear(self) -> None:
        """
        Remove cached chess pieces.

        Does not clear textures from AssetLoader.
        """

        asset_cache.clear_pieces()


# ------------------------------------------------------------
# Global Manager
# ------------------------------------------------------------

chess_piece_manager = ChessPieceManager()