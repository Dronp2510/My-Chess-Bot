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

        self.PROJECT_ROOT = Path(__file__).resolve().parents[2]
        self.PIECE_DIRECTORY = self.PROJECT_ROOT / "Assets" / "Classic"

        self.PIECE_CODES = {
            "king": "k",
            "queen": "q",
            "rook": "r",
            "bishop": "b",
            "knight": "kn",
            "pawn": "p",
        }

        # ----------------------------------------------------
        # Piece metadata
        #
        # This table contains every asset-specific setting.
        # Future themes only need to update this mapping.
        # ----------------------------------------------------

        self.PIECE_METADATA = {

            "white": {

                "king": {
                    "filename": "wk.png",
                    "scale": 0.50,
                },

                "queen": {
                    "filename": "wq.png",
                    "scale": 0.48,
                },

                "rook": {
                    "filename": "wr.png",
                    "scale": 0.42,
                },

                "bishop": {
                    "filename": "wb.png",
                    "scale": 0.44,
                },

                "knight": {
                    "filename": "wkn.png",
                    "scale": 0.46,
                },

                "pawn": {
                    "filename": "wp.png",
                    "scale": 0.34,
                },
            },

            "black": {

                "king": {
                    "filename": "bk.png",
                    "scale": 0.50,
                },

                "queen": {
                    "filename": "bq.png",
                    "scale": 0.48,
                },

                "rook": {
                    "filename": "br.png",
                    "scale": 0.42,
                },

                "bishop": {
                    "filename": "bb.png",
                    "scale": 0.44,
                },

                "knight": {
                    "filename": "bkn.png",
                    "scale": 0.46,
                },

                "pawn": {
                    "filename": "bp.png",
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
        Returns the absolute path to a chess piece in the Classic asset pack.
        """

        color_key = "w" if color == "white" else "b"
        piece_key = self.PIECE_CODES[piece]

        return self.PIECE_DIRECTORY / f"{color_key}{piece_key}.png"

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

        color_key = "w" if color == "white" else "b"
        return f"{color_key}{self.PIECE_CODES[piece]}.png"

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