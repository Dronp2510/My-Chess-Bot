# ============================================================
# File: ui/assets/animations.py
# ============================================================

"""
War Chess
UI-2.A - Asset Pipeline

Animation Loader

Responsibilities
----------------
• Load animations from folders
• Load animations from sprite sheets
• Cache animations
• Store playback metadata
• Never update/play animations

Playback is handled later by AnimatedSprite.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from .constants import SUPPORTED_IMAGE_FORMATS
from .cache import asset_cache
from .loader import asset_loader
from .spritesheet import sprite_sheet_loader


# ============================================================
# Animation Data
# ============================================================

@dataclass(slots=True)
class Animation:
    """
    Immutable animation asset.

    This class contains only animation data.

    It does NOT update itself.
    """

    name: str

    frames: list[pygame.Surface]

    fps: int = 12

    loop: bool = True

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def duration(self) -> float:
        """
        Animation duration in seconds.
        """
        if self.fps <= 0:
            return 0.0

        return self.frame_count / self.fps

    def frame(self, index: int) -> pygame.Surface:
        return self.frames[index]


# ============================================================
# Animation Loader
# ============================================================

class AnimationLoader:

    # --------------------------------------------------------
    # Folder Animation
    # --------------------------------------------------------

    @staticmethod
    def from_folder(
        name: str,
        folder: str | Path,
        fps: int = 12,
        loop: bool = True,
    ) -> Animation:

        if asset_cache.has_animation(name):
            return asset_cache.get_animation(name)

        folder = Path(folder)

        if not folder.exists():
            raise FileNotFoundError(folder)

        frames = []

        files = sorted(
            [
                file
                for file in folder.iterdir()
                if file.suffix.lower()
                in (SUPPORTED_IMAGE_FORMATS)
            ]
        )

        if not files:
            raise ValueError(
                f"No animation frames found:\n{folder}"
            )

        for file in files:
            frames.append(
                asset_loader.load_texture(file)
            )

        animation = Animation(
            name=name,
            frames=frames,
            fps=fps,
            loop=loop,
        )

        asset_cache.store_animation(
            name,
            animation,
        )

        return animation

    # --------------------------------------------------------
    # Sprite Sheet Animation
    # --------------------------------------------------------

    @staticmethod
    def from_sheet(
        name: str,
        sheet_path: str | Path,
        row: int,
        start: int,
        end: int,
        frame_width: int,
        frame_height: int,
        fps: int = 12,
        loop: bool = True,
        margin: int = 0,
        spacing: int = 0,
    ) -> Animation:

        if asset_cache.has_animation(name):
            return asset_cache.get_animation(name)

        sheet = sprite_sheet_loader.load(
            sheet_path
        )

        frames = sheet.strip(
            row=row,
            start=start,
            end=end,
            frame_width=frame_width,
            frame_height=frame_height,
            margin=margin,
            spacing=spacing,
        )

        animation = Animation(
            name=name,
            frames=frames,
            fps=fps,
            loop=loop,
        )

        asset_cache.store_animation(
            name,
            animation,
        )

        return animation

    # --------------------------------------------------------
    # Manual Animation
    # --------------------------------------------------------

    @staticmethod
    def from_frames(
        name: str,
        frames: list[pygame.Surface],
        fps: int = 12,
        loop: bool = True,
    ) -> Animation:

        if asset_cache.has_animation(name):
            return asset_cache.get_animation(name)

        animation = Animation(
            name=name,
            frames=frames,
            fps=fps,
            loop=loop,
        )

        asset_cache.store_animation(
            name,
            animation,
        )

        return animation

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    @staticmethod
    def get(name: str) -> Animation:

        animation = asset_cache.get_animation(
            name
        )

        if animation is None:
            raise KeyError(
                f"Animation '{name}' is not loaded."
            )

        return animation

    @staticmethod
    def exists(name: str) -> bool:
        return asset_cache.has_animation(name)

    @staticmethod
    def unload(name: str):

        asset_cache.remove_animation(name)

    @staticmethod
    def clear():

        asset_cache.clear_animations()


# ------------------------------------------------------------
# Global Loader
# ------------------------------------------------------------

animation_loader = AnimationLoader()