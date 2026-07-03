# ============================================================
# File: ui/assets.py
# ============================================================

"""
War Chess
UI-2.A - Asset Pipeline

Public Asset API

This is the ONLY asset module that should be imported
by the rest of the UI and game.

Example:

    from ui.assets import Assets

    image = Assets.texture(...)
    piece = Assets.piece(...)
    animation = Assets.animation(...)
    button = Assets.button(...)

The implementation behind this API can change without
affecting any other part of the project.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypeAlias

AssetPath: TypeAlias = str | Path
Size: TypeAlias = tuple[int, int]

import pygame

from .resources.loader import asset_loader
from .resources.spritesheet import sprite_sheet_loader
from .resources.animations import animation_loader, Animation
from .resources.chess_cache import chess_piece_manager
from .resources.button_cache import (
    button_skin_manager,
    ButtonSkin,
)
from .resources.cache import asset_cache



class Assets:
    """
    Public façade for the entire UI asset system.
    """

    # =====================================================
    # TEXTURES
    # =====================================================

    @staticmethod
    def texture(
        path: AssetPath,
    ) -> pygame.Surface:
        """
        Load a texture.

        Cached automatically.
        """
        return asset_loader.load_texture(path)

    @staticmethod
    def scaled_texture(
        path: AssetPath,
        size: Size,
    ) -> pygame.Surface:
        """
        Load a scaled texture.

        Each size is cached independently.
        """
        return asset_loader.load_scaled_texture(
            path,
            size,
        )

    # =====================================================
    # SPRITE SHEETS
    # =====================================================

    @staticmethod
    def spritesheet(
        path: AssetPath,
    ):
        """
        Load a sprite sheet.
        """
        return sprite_sheet_loader.load(path)

    # =====================================================
    # ANIMATIONS
    # =====================================================

    @staticmethod
    def animation(
        name: str,
    ) -> Animation:
        """
        Retrieve a cached animation.
        """
        return animation_loader.get(name)

    @staticmethod
    def load_animation_folder(
        name: str,
        folder: AssetPath,
        fps: int = 12,
        loop: bool = True,
    ) -> Animation:

        return animation_loader.from_folder(
            name=name,
            folder=folder,
            fps=fps,
            loop=loop,
        )

    @staticmethod
    def load_animation_sheet(
        name: str,
        sheet_path: AssetPath,
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

        return animation_loader.from_sheet(
            name=name,
            sheet_path=sheet_path,
            row=row,
            start=start,
            end=end,
            frame_width=frame_width,
            frame_height=frame_height,
            fps=fps,
            loop=loop,
            margin=margin,
            spacing=spacing,
        )

    @staticmethod
    def load_animation_frames(
        name: str,
        frames: list[pygame.Surface],
        fps: int = 12,
        loop: bool = True,
    ) -> Animation:

        return animation_loader.from_frames(
            name=name,
            frames=frames,
            fps=fps,
            loop=loop,
        )

    # =====================================================
    # CHESS PIECES
    # =====================================================

    @staticmethod
    def piece(
        color: str,
        piece: str,
    ) -> pygame.Surface:
        """
        Retrieve a chess piece.
        """
        return chess_piece_manager.get(
            color,
            piece,
        )

    @staticmethod
    def scaled_piece(
        color: str,
        piece: str,
        size: Size,
    ) -> pygame.Surface:
        """
        Retrieve a scaled chess piece.
        """
        return chess_piece_manager.get_scaled(
            color,
            piece,
            size,
        )

    @staticmethod
    def preload_pieces() -> None:
        """
        Load every chess piece into memory.
        """
        chess_piece_manager.preload()

    # =====================================================
    # BUTTONS
    # =====================================================

    @staticmethod
    def button(
        name: str,
    ) -> ButtonSkin:
        """
        Retrieve a loaded button skin.
        """
        return button_skin_manager.get(name)

    @staticmethod
    def load_button_sheet(
        name: str,
        sheet_path: AssetPath,
        frame_width: int,
        frame_height: int,
        row: int = 0,
        state_order: tuple[str, ...] = (
            "idle",
            "hover",
            "pressed",
            "disabled",
        ),
        margin: int = 0,
        spacing: int = 0,
    ) -> ButtonSkin:

        return button_skin_manager.from_sheet(
            name=name,
            sheet_path=sheet_path,
            frame_width=frame_width,
            frame_height=frame_height,
            row=row,
            state_order=state_order,
            margin=margin,
            spacing=spacing,
        )

    @staticmethod
    def load_button_images(
        name: str,
        **states,
    ) -> ButtonSkin:

        return button_skin_manager.from_images(
            name=name,
            **states,
        )

    # =====================================================
    # CACHE
    # =====================================================

    @staticmethod
    def clear_cache() -> None:
        """
        Clears every asset cache.
        """
        asset_cache.clear()

    @staticmethod
    def cache_statistics() -> dict[str, int]:
        """
        Returns cache statistics.
        """
        return asset_cache.statistics()

    # =====================================================
    # DEBUG
    # =====================================================

    @staticmethod
    def is_loaded(
        path: AssetPath,
    ) -> bool:

        return asset_loader.is_loaded(path)