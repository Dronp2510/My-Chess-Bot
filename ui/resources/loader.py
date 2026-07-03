# ============================================================
# File: ui/assets/loader.py
# ============================================================

"""
War Chess
UI-2.A - Asset Pipeline

Asset Loader

Responsibilities
----------------
• Load textures from disk
• Validate asset paths
• Cache loaded textures
• Cache scaled textures
• Convert surfaces for fast rendering
• Provide a single loading API

This is the ONLY module that should call
pygame.image.load().
"""

from __future__ import annotations

from pathlib import Path

import pygame

from .cache import asset_cache
from .constants import (
    ENABLE_ASSET_LOGGING,
    LOG_MISSING_ASSETS,
    SUPPORTED_IMAGE_FORMATS,
    USE_SMOOTH_SCALING,
)


class AssetLoader:
    """Loads textures and stores them inside the global asset cache."""

    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------

    @staticmethod
    def _log(message: str) -> None:
        if ENABLE_ASSET_LOGGING:
            print(f"[Assets] {message}")

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    @staticmethod
    def validate_path(path: Path) -> None:
        """
        Ensures that an asset exists and is a supported image.
        """

        if not path.exists():
            if LOG_MISSING_ASSETS:
                raise FileNotFoundError(
                    f"Asset does not exist:\n{path}"
                )

        if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError(
                f"Unsupported asset format: {path.suffix}"
            )

    # --------------------------------------------------------
    # Internal Loading
    # --------------------------------------------------------

    @staticmethod
    def _load_surface(path: Path) -> pygame.Surface:
        """
        Loads an image from disk.
        """

        AssetLoader.validate_path(path)

        surface = pygame.image.load(path).convert_alpha()

        AssetLoader._log(f"Loaded {path.name}")

        return surface

    # --------------------------------------------------------
    # Public Texture Loading
    # --------------------------------------------------------

    @staticmethod
    def load_texture(path: str | Path) -> pygame.Surface:
        """
        Loads a texture and caches it.

        Subsequent requests return the cached texture.
        """

        path = Path(path)

        cache_key = str(path.resolve())

        if asset_cache.has_texture(cache_key):
            return asset_cache.get_texture(cache_key)

        surface = AssetLoader._load_surface(path)

        asset_cache.store_texture(cache_key, surface)

        return surface

    # --------------------------------------------------------
    # Scaled Textures
    # --------------------------------------------------------

    @staticmethod
    def load_scaled_texture(
        path: str | Path,
        size: tuple[int, int],
    ) -> pygame.Surface:
        """
        Loads and scales a texture.

        Every unique size is cached separately.
        """

        width, height = size

        path = Path(path)

        cache_key = str(path.resolve())

        if asset_cache.has_scaled_texture(
            cache_key,
            width,
            height,
        ):
            return asset_cache.get_scaled_texture(
                cache_key,
                width,
                height,
            )

        surface = AssetLoader.load_texture(path)

        if USE_SMOOTH_SCALING:
            scaled = pygame.transform.smoothscale(
                surface,
                size,
            )
        else:
            scaled = pygame.transform.scale(
                surface,
                size,
            )

        asset_cache.store_scaled_texture(
            cache_key,
            width,
            height,
            scaled,
        )

        return scaled

    # --------------------------------------------------------
    # Cache Queries
    # --------------------------------------------------------

    @staticmethod
    def is_loaded(path: str | Path) -> bool:

        path = Path(path)

        return asset_cache.has_texture(
            str(path.resolve())
        )

    @staticmethod
    def unload(path: str | Path) -> None:
        """
        Removes a texture from the cache.

        Mostly useful during development.
        """

        path = Path(path)

        key = str(path.resolve())

        asset_cache.remove_texture(key)

    @staticmethod
    def clear() -> None:
        """
        Clears the complete asset cache.
        """

        asset_cache.clear()

    @staticmethod
    def statistics() -> dict[str, int]:
        """
        Returns cache statistics.
        """

        return asset_cache.statistics()


# ------------------------------------------------------------
# Global Loader Instance
# ------------------------------------------------------------

asset_loader = AssetLoader()