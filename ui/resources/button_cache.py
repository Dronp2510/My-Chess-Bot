# ============================================================
# File: ui/assets/button_cache.py
# ============================================================

"""
War Chess
UI-2.A - Asset Pipeline

Button Skin Cache

Responsibilities
----------------
• Load button skins
• Cache button states
• Support sprite sheets
• Support individual textures
• Future-proof for additional states

UI widgets should never know where button assets
come from. They simply request a ButtonSkin.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame

from .cache import asset_cache
from .loader import asset_loader
from .spritesheet import sprite_sheet_loader


# ============================================================
# Button Skin
# ============================================================

@dataclass(slots=True)
class ButtonSkin:
    """
    Represents every visual state of a button.
    """

    name: str

    states: dict[str, pygame.Surface] = field(default_factory=dict)

    def add_state(
        self,
        state: str,
        surface: pygame.Surface,
    ) -> None:

        self.states[state] = surface

    def get(
        self,
        state: str,
    ) -> pygame.Surface:

        if state not in self.states:
            raise KeyError(
                f"Button '{self.name}' has no state '{state}'."
            )

        return self.states[state]

    def has(
        self,
        state: str,
    ) -> bool:

        return state in self.states

    @property
    def available_states(self) -> tuple[str, ...]:
        return tuple(self.states.keys())


# ============================================================
# Button Skin Manager
# ============================================================

class ButtonSkinManager:

    # --------------------------------------------------------
    # Individual Images
    # --------------------------------------------------------

    @staticmethod
    def from_images(
        name: str,
        **states: str | Path,
    ) -> ButtonSkin:

        if asset_cache.has_button(name):
            return asset_cache.get_button(name)

        skin = ButtonSkin(name)

        for state, path in states.items():

            surface = asset_loader.load_texture(path)

            skin.add_state(
                state,
                surface,
            )

        asset_cache.store_button(
            name,
            skin,
        )

        return skin

    # --------------------------------------------------------
    # Sprite Sheet
    # --------------------------------------------------------

    @staticmethod
    def from_sheet(
        name: str,
        sheet_path: str | Path,
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

        if asset_cache.has_button(name):
            return asset_cache.get_button(name)

        sheet = sprite_sheet_loader.load(sheet_path)

        skin = ButtonSkin(name)

        for column, state in enumerate(state_order):

            surface = sheet.grid_frame(
                column=column,
                row=row,
                frame_width=frame_width,
                frame_height=frame_height,
                margin=margin,
                spacing=spacing,
            )

            skin.add_state(
                state,
                surface,
            )

        asset_cache.store_button(
            name,
            skin,
        )

        return skin

    # --------------------------------------------------------
    # Lookup
    # --------------------------------------------------------

    @staticmethod
    def get(
        name: str,
    ) -> ButtonSkin:

        skin = asset_cache.get_button(name)

        if skin is None:
            raise KeyError(
                f"Button skin '{name}' has not been loaded."
            )

        return skin

    @staticmethod
    def exists(
        name: str,
    ) -> bool:

        return asset_cache.has_button(name)

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    @staticmethod
    def unload(
        name: str,
    ) -> None:

        asset_cache.remove_button(name)

    @staticmethod
    def clear() -> None:

        asset_cache.clear_buttons()


# ------------------------------------------------------------
# Global Manager
# ------------------------------------------------------------

button_skin_manager = ButtonSkinManager()