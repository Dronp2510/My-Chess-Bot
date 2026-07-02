"""
assets.py
=========

Global Asset Manager for War Chess.

Responsibilities
----------------
• Locate the project's asset directory
• Load and cache images
• Load and cache fonts
• Prevent duplicate asset loading
• Provide a single interface for all UI assets

IMPORTANT
---------
Widgets and screens should NEVER call pygame.image.load()
or pygame.font.Font() directly.

Always use the global `assets` instance.

Future versions of this manager will also support:

    - Audio
    - Sprite atlases
    - Animation sheets
    - Nine-slice textures
    - Async loading
    - Loading screens
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame


# ============================================================
# Asset Manager
# ============================================================


class AssetManager:
    """
    Global asset cache.

    Every image, font and sound should be requested
    through this manager.

    Assets are loaded exactly once.
    """

    def __init__(self) -> None:

        self._initialized = False

        self.project_root = self._discover_project_root()

        self.asset_root = self._discover_asset_directory()

        self._image_cache: Dict[Tuple[str, Optional[Tuple[int, int]]], pygame.Surface] = {}

        self._font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}

    # --------------------------------------------------------
    # Initialization
    # --------------------------------------------------------

    def initialize(self) -> None:
        """
        Initializes pygame font module if necessary.

        Safe to call multiple times.
        """

        if self._initialized:
            return

        if not pygame.font.get_init():
            pygame.font.init()

        self._initialized = True

    # ========================================================
    # Project Discovery
    # ========================================================

    def _discover_project_root(self) -> Path:
        """
        Attempts to locate the project root.

        assets.py lives inside:

            Project/ui/assets.py

        Therefore parent.parent should always be the root.
        """

        return Path(__file__).resolve().parent.parent

    def _discover_asset_directory(self) -> Path:
        """
        Locate Assets/ or assets/.

        Raises
        ------
        FileNotFoundError
            If neither directory exists.
        """

        candidates = [
            self.project_root / "Assets",
            self.project_root / "assets",
        ]

        for folder in candidates:
            if folder.exists():
                return folder

        raise FileNotFoundError(
            "Unable to locate Assets/ directory."
        )

    # ========================================================
    # Path Helpers
    # ========================================================

    def asset_path(self, relative_path: str) -> Path:
        """
        Returns an absolute path inside Assets.

        Example
        -------

        assets.asset_path("ui/button.png")
        """

        return self.asset_root / relative_path

    def exists(self, relative_path: str) -> bool:
        """
        Returns True if an asset exists.
        """

        return self.asset_path(relative_path).exists()

    # ========================================================
    # Images
    # ========================================================

    def load_image(
        self,
        relative_path: str,
        size: Optional[Tuple[int, int]] = None,
        alpha: bool = True,
    ) -> pygame.Surface:
        """
        Load an image from disk.

        Results are cached automatically.

        Parameters
        ----------
        relative_path
            Path relative to Assets/

        size
            Optional resize.

        alpha
            Preserve transparency.
        """

        cache_key = (relative_path, size)

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        path = self.asset_path(relative_path)

        if not path.exists():
            raise FileNotFoundError(path)

        image = pygame.image.load(str(path))

        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()

        if size is not None:
            image = pygame.transform.smoothscale(
                image,
                size,
            )

        self._image_cache[cache_key] = image

        return image

    # ========================================================
    # Fonts
    # ========================================================

    def load_font(
        self,
        font_name: str,
        size: int,
    ) -> pygame.font.Font:
        """
        Load a font.

        If font_name is unavailable on the system,
        pygame will gracefully fall back.
        """

        self.initialize()

        cache_key = (font_name, size)

        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        font = pygame.font.SysFont(
            font_name,
            size,
        )

        self._font_cache[cache_key] = font

        return font

    # ========================================================
    # Convenience
    # ========================================================

    def image(
        self,
        relative_path: str,
        size: Optional[Tuple[int, int]] = None,
    ) -> pygame.Surface:
        """
        Alias for load_image().
        """

        return self.load_image(
            relative_path,
            size=size,
        )

    def font(
        self,
        font_name: str,
        size: int,
    ) -> pygame.font.Font:
        """
        Alias for load_font().
        """

        return self.load_font(
            font_name,
            size,
        )

    # ========================================================
    # Cache Information
    # ========================================================

    @property
    def image_count(self) -> int:
        """
        Number of cached images.
        """

        return len(self._image_cache)

    @property
    def font_count(self) -> int:
        """
        Number of cached fonts.
        """

        return len(self._font_cache)

# ============================================================
# Sounds
# ============================================================

    def load_sound(
        self,
        relative_path: str,
    ) -> pygame.mixer.Sound:
        """
        Load a sound effect.

        Sounds are cached automatically.
        """

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        if not hasattr(self, "_sound_cache"):
            self._sound_cache: Dict[str, pygame.mixer.Sound] = {}

        if relative_path in self._sound_cache:
            return self._sound_cache[relative_path]

        path = self.asset_path(relative_path)

        if not path.exists():
            raise FileNotFoundError(path)

        sound = pygame.mixer.Sound(str(path))

        self._sound_cache[relative_path] = sound

        return sound


# ============================================================
# Preloading
# ============================================================

    def preload_images(
        self,
        assets: list[str],
    ) -> None:
        """
        Preload multiple images.
        """

        for asset in assets:
            self.load_image(asset)

    def preload_sounds(
        self,
        assets: list[str],
    ) -> None:
        """
        Preload multiple sounds.
        """

        for asset in assets:
            self.load_sound(asset)


# ============================================================
# Cache Management
# ============================================================

    def clear_image_cache(self) -> None:

        self._image_cache.clear()

    def clear_font_cache(self) -> None:

        self._font_cache.clear()

    def clear_sound_cache(self) -> None:

        if hasattr(self, "_sound_cache"):
            self._sound_cache.clear()

    def clear(self) -> None:
        """
        Clear every cache.
        """

        self.clear_image_cache()
        self.clear_font_cache()
        self.clear_sound_cache()


# ============================================================
# Statistics
# ============================================================

    @property
    def sound_count(self) -> int:

        if not hasattr(self, "_sound_cache"):
            return 0

        return len(self._sound_cache)

    @property
    def total_cached_assets(self) -> int:

        return (
            self.image_count
            + self.font_count
            + self.sound_count
        )


# ============================================================
# Validation
# ============================================================

    def validate_asset(
        self,
        relative_path: str,
    ) -> bool:
        """
        Returns True if an asset exists.
        """

        return self.asset_path(relative_path).exists()


# ============================================================
# Future Atlas Hooks
# ============================================================

    def load_sprite_atlas(
        self,
        relative_path: str,
    ) -> pygame.Surface:
        """
        Placeholder for future sprite atlas support.

        Currently behaves exactly like load_image().
        """

        return self.load_image(relative_path)

    def load_nine_slice(
        self,
        relative_path: str,
    ) -> pygame.Surface:
        """
        Placeholder for future nine-slice support.

        Currently behaves exactly like load_image().
        """

        return self.load_image(relative_path)


# ============================================================
# Theme Font Helpers
# ============================================================

    def title_font(self, theme):

        return self.font(
            theme.typography.font_name,
            theme.typography.title_size,
        )

    def heading_font(self, theme):

        return self.font(
            theme.typography.font_name,
            theme.typography.heading_size,
        )

    def subheading_font(self, theme):

        return self.font(
            theme.typography.font_name,
            theme.typography.subheading_size,
        )

    def body_font(self, theme):

        return self.font(
            theme.typography.font_name,
            theme.typography.body_size,
        )

    def caption_font(self, theme):

        return self.font(
            theme.typography.font_name,
            theme.typography.caption_size,
        )

    def small_font(self, theme):

        return self.font(
            theme.typography.font_name,
            theme.typography.small_size,
        )


# ============================================================
# Debug
# ============================================================

    def cache_statistics(self) -> dict[str, int]:
        """
        Returns cache information useful for debugging.
        """

        return {
            "images": self.image_count,
            "fonts": self.font_count,
            "sounds": self.sound_count,
            "total": self.total_cached_assets,
        }


# ============================================================
# Convenience Functions
# ============================================================


def image(
    relative_path: str,
    size: Optional[Tuple[int, int]] = None,
) -> pygame.Surface:
    return assets.image(relative_path, size)


def font(
    font_name: str,
    size: int,
) -> pygame.font.Font:
    return assets.font(font_name, size)


def sound(
    relative_path: str,
) -> pygame.mixer.Sound:
    return assets.load_sound(relative_path)

# ============================================================
# Global Singleton
# ============================================================

assets = AssetManager()


__all__ = [
    "AssetManager",
    "assets",
    "image",
    "font",
    "sound",
]