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

    A SpriteSheet is simply a wrapper around a pygame.Surface
    with helper methods for extracting frames.
    """

    def __init__(self, image: pygame.Surface):

        self.image = image

        self.width = image.get_width()
        self.height = image.get_height()

    # ---------------------------------------------------------
    # Single Frame
    # ---------------------------------------------------------

    def frame(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> pygame.Surface:
        """
        Extracts a single frame.
        """

        surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        surface.blit(
            self.image,
            (0, 0),
            pygame.Rect(x, y, width, height),
        )

        return surface.convert_alpha()

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