# ============================================================
# File: ui/assets/cache.py
# ============================================================

"""
War Chess
UI-2.A - Asset Pipeline

Texture Cache

Responsibilities
----------------
• Store loaded textures
• Store scaled texture variants
• Store sprite sheets
• Store animations
• Store chess pieces
• Store button states
• Provide cache statistics
• Clear caches safely

This module NEVER loads files from disk.
Loading is handled by loader.py.
"""

from __future__ import annotations

from typing import Any


class AssetCache:
    """
    Central cache used by the UI asset system.

    Every expensive object should only exist once in memory.
    """

    def __init__(self) -> None:

        # Raw pygame.Surface objects
        self._textures: dict[str, Any] = {}

        # (path, width, height) -> Surface
        self._scaled_textures: dict[tuple[str, int, int], Any] = {}

        # path -> SpriteSheet
        self._spritesheets: dict[str, Any] = {}

        # animation_name -> list[Surface]
        self._animations: dict[str, Any] = {}

        # (color, piece) -> Surface
        self._chess_pieces: dict[tuple[str, str], Any] = {}

        # button_name -> ButtonStates
        self._buttons: dict[str, Any] = {}

        # font cache (implemented later)
        self._fonts: dict[Any, Any] = {}

    # =========================================================
    # TEXTURES
    # =========================================================

    def has_texture(self, path: str) -> bool:
        return path in self._textures

    def get_texture(self, path: str):

        return self._textures.get(path)

    def store_texture(self, path: str, surface) -> None:

        self._textures[path] = surface

    def remove_texture(self, path: str) -> None:

        self._textures.pop(path, None)

    # =========================================================
    # SCALED TEXTURES
    # =========================================================

    def _scaled_key(
        self,
        path: str,
        width: int,
        height: int
    ) -> tuple[str, int, int]:

        return (path, width, height)

    def has_scaled_texture(
        self,
        path: str,
        width: int,
        height: int
    ) -> bool:

        return self._scaled_key(path, width, height) in self._scaled_textures

    def get_scaled_texture(
        self,
        path: str,
        width: int,
        height: int
    ):

        return self._scaled_textures.get(
            self._scaled_key(path, width, height)
        )

    def store_scaled_texture(
        self,
        path: str,
        width: int,
        height: int,
        surface,
    ) -> None:

        self._scaled_textures[
            self._scaled_key(path, width, height)
        ] = surface

    # =========================================================
    # SPRITE SHEETS
    # =========================================================

    def has_spritesheet(self, path: str) -> bool:
        return path in self._spritesheets

    def get_spritesheet(self, path: str):

        return self._spritesheets.get(path)

    def store_spritesheet(self, path: str, sheet) -> None:

        self._spritesheets[path] = sheet

    def remove_spritesheet(self, path: str) -> None:

        self._spritesheets.pop(path, None)

    # =========================================================
    # ANIMATIONS
    # =========================================================

    def has_animation(self, name: str) -> bool:
        return name in self._animations

    def get_animation(self, name: str):

        return self._animations.get(name)

    def store_animation(self, name: str, frames) -> None:

        self._animations[name] = frames

    def remove_animation(self, name: str) -> None:

        self._animations.pop(name, None)

    def clear_animations(self) -> None:

        self._animations.clear()

    # =========================================================
    # CHESS PIECES
    # =========================================================

    def has_piece(
        self,
        color: str,
        piece: str,
    ) -> bool:

        return (color, piece) in self._chess_pieces

    def get_piece(
        self,
        color: str,
        piece: str,
    ):

        return self._chess_pieces.get((color, piece))

    def store_piece(
        self,
        color: str,
        piece: str,
        surface,
    ) -> None:

        self._chess_pieces[(color, piece)] = surface

    def clear_pieces(self) -> None:

        self._chess_pieces.clear()

    # =========================================================
    # BUTTONS
    # =========================================================

    def has_button(self, name: str) -> bool:
        return name in self._buttons

    def get_button(self, name: str):

        return self._buttons.get(name)

    def store_button(
        self,
        name: str,
        states,
    ) -> None:

        self._buttons[name] = states

    def remove_button(self, name: str) -> None:

        self._buttons.pop(name, None)


    def clear_buttons(self) -> None:
        
        self._buttons.clear()

    # =========================================================
    # FONTS
    # =========================================================

    def has_font(self, key) -> bool:
        return key in self._fonts

    def get_font(self, key):

        return self._fonts.get(key)

    def store_font(
        self,
        key,
        font,
    ) -> None:

        self._fonts[key] = font

    # =========================================================
    # CACHE MANAGEMENT
    # =========================================================

    def clear(self) -> None:
        """
        Clears every cache.
        """

        self._textures.clear()
        self._scaled_textures.clear()
        self._spritesheets.clear()
        self._animations.clear()
        self._chess_pieces.clear()
        self._buttons.clear()
        self._fonts.clear()

    def texture_count(self) -> int:
        return len(self._textures)

    def scaled_texture_count(self) -> int:
        return len(self._scaled_textures)

    def spritesheet_count(self) -> int:
        return len(self._spritesheets)

    def animation_count(self) -> int:
        return len(self._animations)

    def chess_piece_count(self) -> int:
        return len(self._chess_pieces)

    def button_count(self) -> int:
        return len(self._buttons)

    def font_count(self) -> int:
        return len(self._fonts)

    def total_cached_objects(self) -> int:
        """
        Returns the total number of cached objects.
        """

        return (
            self.texture_count()
            + self.scaled_texture_count()
            + self.spritesheet_count()
            + self.animation_count()
            + self.chess_piece_count()
            + self.button_count()
            + self.font_count()
        )

    def statistics(self) -> dict[str, int]:
        """
        Returns cache statistics for debugging.
        """

        return {
            "textures": self.texture_count(),
            "scaled_textures": self.scaled_texture_count(),
            "spritesheets": self.spritesheet_count(),
            "animations": self.animation_count(),
            "pieces": self.chess_piece_count(),
            "buttons": self.button_count(),
            "fonts": self.font_count(),
            "total": self.total_cached_objects(),
        }


# ------------------------------------------------------------
# Global Cache Instance
# ------------------------------------------------------------

asset_cache = AssetCache()