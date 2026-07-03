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
from .loader import asset_loader
from .constants import (
    CHESS_ASSETS_DIR,
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
    # Path Resolution
    # --------------------------------------------------------

    def _piece_path(
        self,
        color: str,
        piece: str,
    ) -> Path:
        """
        Default naming convention:

            Chess/
                default/
                    white/
                        king.png
                        queen.png
                    black/
                        king.png
                        queen.png
        """

        return (
            CHESS_ASSETS_DIR
            / self.theme
            / color
            / f"{piece}.png"
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

        path = self._piece_path(
            color,
            piece,
        )

        return asset_loader.load_scaled_texture(
            path,
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