# ============================================================
# File: ui/assets/chess_cache.py
# ============================================================

"""
War Chess
UI Polish-1

Production Chess Piece Cache

Responsibilities
----------------
• Load themed chess piece PNGs
• Cache loaded assets
• Provide scaled variants
• Keep the public API stable
• Support future themes

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
from .loader import asset_loader


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

        self.PIECE_DIRECTORY = (
            Path("Assets")
            / "Generated_assets"
            / "Themed_pieces"
        )

        # ----------------------------------------------------
        # Piece metadata
        #
        # This table contains every asset-specific setting.
        # Future themes only need to update this mapping.
        # ----------------------------------------------------

        self.PIECE_METADATA = {

            "white": {

                "king": {
                    "filename": "White_king.png",
                    "scale": 0.50,
                },

                "queen": {
                    "filename": "White_queen.png",
                    "scale": 0.48,
                },

                "rook": {
                    "filename": "White_rook.png",
                    "scale": 0.42,
                },

                "bishop": {
                    "filename": "White_bishop.png",
                    "scale": 0.44,
                },

                "knight": {
                    "filename": "White_knight.png",
                    "scale": 0.46,
                },

                "pawn": {
                    "filename": "White_pawn.png",
                    "scale": 0.34,
                },
            },

            "black": {

                "king": {
                    "filename": "Black_king.png",
                    "scale": 0.50,
                },

                "queen": {
                    "filename": "Black_queen.png",
                    "scale": 0.48,
                },

                "rook": {
                    "filename": "Black_rook.png",
                    "scale": 0.42,
                },

                "bishop": {
                    "filename": "Black_bishop.png",
                    "scale": 0.44,
                },

                "knight": {
                    "filename": "Black_knight.png",
                    "scale": 0.46,
                },

                "pawn": {
                    "filename": "Black_pawn.png",
                    "scale": 0.34,
                },
            },
        }

    # --------------------------------------------------------
    # Internal
    # --------------------------------------------------------

    # def _atlas(self):

    #     if self.sheet is None:
    #         self.sheet = sprite_sheet_loader.load(
    #             self.ATLAS_PATH
    #         )

    #     return self.sheet

    # --------------------------------------------------------
    # Internal Helpers
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
                f"Unknown piece: {piece}"
            )

    def _piece_path(
        self,
        color: str,
        piece: str,
    ) -> Path:
        """
        Returns the absolute path to a themed chess piece.
        """

        filename = self.PIECE_METADATA[color][piece]["filename"]

        return (
            self.PIECE_DIRECTORY
            / color
            / filename
        )

    # --------------------------------------------------------
    # Loading
    # --------------------------------------------------------

    def load(
        self,
        color: str,
        piece: str,
    ) -> pygame.Surface:

        self._validate(
            color,
            piece,
        )

        cached = asset_cache.get_piece(
            color,
            piece,
        )

        if cached is not None:
            return cached

        surface = asset_loader.load_texture(
            self._piece_path(
                color,
                piece,
            )
        )

        asset_cache.store_piece(
            color,
            piece,
            surface,
        )

        return surface

    # --------------------------------------------------------
    # Bulk Preload
    # --------------------------------------------------------

    def preload(self) -> None:

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

        self._validate(
            color,
            piece,
        )

        surface = asset_cache.get_piece(
            color,
            piece,
        )

        if surface is None:
            surface = self.load(
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
        """
        Returns a scaled version of a chess piece.

        The supplied size represents the desired bounding-box
        size. Each piece then applies its own optical scale so
        that all rendered pieces appear visually balanced.
        """

        surface = self.get(
            color,
            piece,
        )

        scale = self.PIECE_METADATA[color][piece]["scale"]

        width = max(
            1,
            round(size[0] * scale),
        )

        height = max(
            1,
            round(size[1] * scale),
        )

        return pygame.transform.smoothscale(
            surface,
            (width, height),
        )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    def get_base_scale(
        self,
        piece: str,
    ) -> float:
        """
        Returns the default optical scale for a piece.

        The current assets use identical geometry for both colors,
        so the white metadata is used as the canonical source.
        """

        if piece not in PIECE_NAMES:
            raise ValueError(
                f"Unknown piece: {piece}"
            )

        return self.PIECE_METADATA["white"][piece]["scale"]

    def get_filename(
        self,
        color: str,
        piece: str,
    ) -> str:

        self._validate(
            color,
            piece,
        )

        return self.PIECE_METADATA[color][piece]["filename"]

    # --------------------------------------------------------
    # Theme
    # --------------------------------------------------------

    def set_theme(
        self,
        theme: str,
    ) -> None:
        """
        Reserved for future themed piece packs.
        """

        self.theme = theme

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    def clear(self) -> None:

        asset_cache.clear_pieces()


# ------------------------------------------------------------
# Global Manager
# ------------------------------------------------------------

chess_piece_manager = ChessPieceManager()