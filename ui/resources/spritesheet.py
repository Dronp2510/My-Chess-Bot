# ============================================================
# File: ui/assets/spritesheet.py
# ============================================================

"""
War Chess
UI-2.A - Asset Pipeline

Sprite Sheet Helper

Responsibilities
----------------
• Slice sprite sheets
• Cache extracted frames
• Support margins and spacing
• Support manual frame extraction
• Support row/column lookup
• Support animation strip extraction

SpriteSheet never loads images itself.
Images are provided by AssetLoader.
"""

from __future__ import annotations

from pathlib import Path

import pygame

from .cache import asset_cache
from .loader import asset_loader


class SpriteSheet:
    """
    Represents a loaded sprite sheet.

    Besides simple frame extraction, this class now supports
    production-quality sprite processing including automatic
    trimming and optional padding.

    All expensive processing occurs once during loading and the
    processed surfaces are cached by ChessPieceManager.
    """

    def __init__(self, image: pygame.Surface):

        self.image = image

        self.width = image.get_width()
        self.height = image.get_height()

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _trim_alpha(
        surface: pygame.Surface,
    ) -> pygame.Surface:
        """
        Remove fully transparent borders.

        Uses pygame's alpha bounding box detection.

        If no visible pixels exist, the original
        surface is returned.
        """

        rect = surface.get_bounding_rect()

        if rect.width == 0 or rect.height == 0:
            return surface

        trimmed = pygame.Surface(
            rect.size,
            pygame.SRCALPHA,
        )

        trimmed.blit(
            surface,
            (0, 0),
            rect,
        )

        return trimmed.convert_alpha()
    
    @staticmethod
    def _remove_black_background(
        surface: pygame.Surface,
        *,
        threshold: int = 18,
    ) -> pygame.Surface:
        """
        Converts near-black background pixels into transparency.

        This is intended for artwork exported on an opaque black
        background while preserving the dark details of the pieces.

        Any pixel whose RGB values are all <= threshold becomes
        fully transparent.
        """

        result = surface.copy()

        width, height = result.get_size()

        for y in range(height):
            for x in range(width):

                r, g, b, a = result.get_at((x, y))

                if (
                    r <= threshold
                    and g <= threshold
                    and b <= threshold
                ):
                    result.set_at(
                        (x, y),
                        (0, 0, 0, 0),
                    )

        return result.convert_alpha()
    
    @staticmethod
    def _add_padding(
        surface: pygame.Surface,
        padding: int,
    ) -> pygame.Surface:

        if padding <= 0:
            return surface

        w = surface.get_width() + padding * 2
        h = surface.get_height() + padding * 2

        padded = pygame.Surface(
            (w, h),
            pygame.SRCALPHA,
        )

        padded.blit(
            surface,
            (padding, padding),
        )

        return padded.convert_alpha()

    # ---------------------------------------------------------
    # Single Frame
    # ---------------------------------------------------------

    def frame(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        trim: bool = False,
        padding: int = 0,
    ) -> pygame.Surface:
        """
        Extract a frame.

        Parameters
        ----------
        trim:
            Automatically remove transparent borders.

        padding:
            Re-add transparent padding after trimming.

        These options are optional to preserve backwards
        compatibility with existing callers.
        """

        surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        surface.blit(
            self.image,
            (0, 0),
            pygame.Rect(
                x,
                y,
                width,
                height,
            ),
        )

        surface = surface.convert_alpha()

        surface = surface.convert_alpha()

        #
        # The chess atlas ships with an opaque black background.
        # Remove it before trimming.
        #

        surface = self._remove_black_background(surface)

        if trim:
            surface = self._trim_alpha(surface)

        if padding:
            surface = self._add_padding(
                surface,
                padding,
            )

        return surface

    # ---------------------------------------------------------
    # Grid Frame
    # ---------------------------------------------------------

    def grid_frame(
        self,
        column: int,
        row: int,
        frame_width: int,
        frame_height: int,
        margin: int = 0,
        spacing: int = 0,
    ) -> pygame.Surface:
        """
        Extract frame using grid coordinates.
        """

        x = margin + column * (frame_width + spacing)

        y = margin + row * (frame_height + spacing)

        return self.frame(
            x,
            y,
            frame_width,
            frame_height,
        )

    # ---------------------------------------------------------
    # Entire Row
    # ---------------------------------------------------------

    def row(
        self,
        row: int,
        frame_width: int,
        frame_height: int,
        margin: int = 0,
        spacing: int = 0,
    ) -> list[pygame.Surface]:
        """
        Extract every frame from one row.
        """

        frames = []

        columns = (
            self.width - margin + spacing
        ) // (frame_width + spacing)

        for col in range(columns):

            frames.append(
                self.grid_frame(
                    col,
                    row,
                    frame_width,
                    frame_height,
                    margin,
                    spacing,
                )
            )

        return frames

    # ---------------------------------------------------------
    # Entire Column
    # ---------------------------------------------------------

    def column(
        self,
        column: int,
        frame_width: int,
        frame_height: int,
        margin: int = 0,
        spacing: int = 0,
    ) -> list[pygame.Surface]:

        frames = []

        rows = (
            self.height - margin + spacing
        ) // (frame_height + spacing)

        for row in range(rows):

            frames.append(
                self.grid_frame(
                    column,
                    row,
                    frame_width,
                    frame_height,
                    margin,
                    spacing,
                )
            )

        return frames

    # ---------------------------------------------------------
    # Whole Sheet
    # ---------------------------------------------------------

    def grid(
        self,
        frame_width: int,
        frame_height: int,
        margin: int = 0,
        spacing: int = 0,
    ) -> list[pygame.Surface]:
        """
        Slice the entire sheet.
        """

        frames = []

        rows = (
            self.height - margin + spacing
        ) // (frame_height + spacing)

        cols = (
            self.width - margin + spacing
        ) // (frame_width + spacing)

        for row in range(rows):

            for col in range(cols):

                frames.append(
                    self.grid_frame(
                        col,
                        row,
                        frame_width,
                        frame_height,
                        margin,
                        spacing,
                    )
                )

        return frames

    # ---------------------------------------------------------
    # Animation Strip
    # ---------------------------------------------------------

    def strip(
        self,
        row: int,
        frame_width: int,
        frame_height: int,
        start: int,
        end: int,
        margin: int = 0,
        spacing: int = 0,
    ) -> list[pygame.Surface]:
        """
        Extract a continuous animation strip.
        """

        frames = []

        for col in range(start, end + 1):

            frames.append(
                self.grid_frame(
                    col,
                    row,
                    frame_width,
                    frame_height,
                    margin,
                    spacing,
                )
            )

        return frames


# ============================================================
# SpriteSheet Loader
# ============================================================

class SpriteSheetLoader:
    """
    Handles loading and caching SpriteSheet objects.
    """

    @staticmethod
    def load(path: str | Path) -> SpriteSheet:

        path = Path(path)

        key = str(path.resolve())

        if asset_cache.has_spritesheet(key):

            return asset_cache.get_spritesheet(key)

        image = asset_loader.load_texture(path)

        sheet = SpriteSheet(image)

        asset_cache.store_spritesheet(
            key,
            sheet,
        )

        return sheet

    @staticmethod
    def unload(path: str | Path):

        path = Path(path)

        key = str(path.resolve())

        asset_cache.remove_spritesheet(key)


# -------------------------------------------------------------
# Global Loader
# -------------------------------------------------------------

sprite_sheet_loader = SpriteSheetLoader()