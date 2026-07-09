"""
button.py

Production-ready button widget used throughout the UI framework.

Features
--------
- Hover state
- Press state
- Disabled state
- Mouse enter/leave callbacks
- Click callback
- Parent-aware coordinates
- Animation-ready
"""

from __future__ import annotations

from typing import Callable, Optional

import pygame
from ui.resources.button_cache import ButtonSkin

from .widget import Widget
from ui.animation.animator import Animator


class Button(Widget):
    """
    Base interactive button.

    Rendering is intentionally generic.
    Visual styling will later come from
    sprite-sheet skins.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = "",
        skin: ButtonSkin | None = None,
        on_click=None,
        enabled: bool = True,
        visible: bool = True,
    ) -> None:

        super().__init__(
            x,
            y,
            width,
            height,
        )

        self.text = text

        #
        # Optional themed button skin.
        #
        self.skin = skin

        #
        # Cache of scaled button images.
        #
        self._scaled_states: dict[str, pygame.Surface] = {}

        #
        # Tracks the size used to build the cache.
        #
        self._cached_size = (width, height)

        if self.skin is not None:
            self._rebuild_skin_cache()

        self.enabled = enabled
        self.visible = visible

        self.on_click = on_click

        self.hovered = False
        self.pressed = False
        self.focused = False

        self.animator = Animator()

        self.on_hover_enter: Optional[Callable[[], None]] = None
        self.on_hover_exit: Optional[Callable[[], None]] = None

        #
        # Temporary font.
        # Later this will come from the asset pipeline.
        #
        self.font = pygame.font.SysFont(
            "arial",
            28,
            bold=True,
        )

    # ======================================================
    # Button Skin
    # ======================================================

    def set_skin(
        self,
        skin: ButtonSkin | None,
    ) -> None:
        """
        Assign or replace the button skin.
        """

        self.skin = skin
        self._rebuild_skin_cache()

    def _rebuild_skin_cache(self) -> None:
        """
        Builds scaled images while preserving the
        original aspect ratio.
        """

        self._scaled_states.clear()

        if self.skin is None:
            return

        max_width = self.width
        max_height = self.height

        for state in self.skin.available_states:

            image = self.skin.get(state)

            original_width = image.get_width()
            original_height = image.get_height()

            scale = min(
                max_width / original_width,
                max_height / original_height,
            )

            new_width = max(1, int(original_width * scale))
            new_height = max(1, int(original_height * scale))

            scaled = pygame.transform.smoothscale(
                image,
                (new_width, new_height),
            )

            self._scaled_states[state] = scaled

        self._cached_size = (
            max_width,
            max_height,
        )

    def _current_image(self) -> pygame.Surface | None:
        """
        Returns the correct image for the
        current button state.
        """

        if self.skin is None:
            return None

        #
        # Button resized?
        #

        if self._cached_size != (self.width, self.height):
            self._rebuild_skin_cache()

        #
        # Exact state exists.
        #

        if self.state in self._scaled_states:
            return self._scaled_states[self.state]

        #
        # Disabled missing?
        #

        if self.state == "disabled":

            if "idle" in self._scaled_states:

                image = self._scaled_states["idle"].copy()

                image.set_alpha(140)

                return image

        #
        # Fallback.
        #

        return self._scaled_states.get("idle")
    
    # ======================================================
    # State
    # ======================================================

    @property
    def state(self) -> str:

        if not self.enabled:
            return "disabled"

        if self.pressed:
            return "pressed"

        if self.hovered:
            return "hover"

        return "idle"

    # ======================================================
    # Public API
    # ======================================================

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:

        self.enabled = False
        self.hovered = False
        self.pressed = False

    def set_callback(
        self,
        callback: Optional[Callable[[], None]],
    ) -> None:

        self.on_click = callback

    # ======================================================
    # Events
    # ======================================================

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> bool:

        #
        # Give children first chance.
        #

        if super().handle_event(event):
            return True

        if not self.enabled or not self.visible:
            return False

        rect = self.global_rect

        if event.type == pygame.MOUSEMOTION:

            was_hovered = self.hovered

            self.hovered = rect.collidepoint(event.pos)

            if self.hovered and not was_hovered:

                if self.on_hover_enter:
                    self.on_hover_enter()

            elif was_hovered and not self.hovered:

                if self.on_hover_exit:
                    self.on_hover_exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1 and self.hovered:

                self.pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                clicked = self.pressed and self.hovered

                self.pressed = False

                if clicked:

                    if self.on_click:
                        self.on_click()

                    return True

        return False

    # ======================================================
    # Update
    # ======================================================

    def update(
        self,
        dt: float,
    ) -> None:

        super().update(dt)

    # ======================================================
    # Draw
    # ======================================================

    def draw(
        self,
        surface: pygame.Surface,
    ) -> None:

        if not self.visible:
            return

        rect = self.global_rect

        #
        # --------------------------------------------------
        # Themed Button Rendering
        # --------------------------------------------------
        #

        image = self._current_image()

        if image is not None:

            image_rect = image.get_rect(
                center=rect.center,
            )

            surface.blit(
                image,
                image_rect,
            )

            return

        #
        # --------------------------------------------------
        # Fallback Rendering
        # (Current placeholder implementation)
        # --------------------------------------------------
        #

        colors = {
            "idle": (70, 70, 70),
            "hover": (95, 95, 95),
            "pressed": (45, 45, 45),
            "disabled": (35, 35, 35),
        }

        pygame.draw.rect(
            surface,
            colors[self.state],
            rect,
            border_radius=8,
        )

        pygame.draw.rect(
            surface,
            (180, 180, 180),
            rect,
            width=2,
            border_radius=8,
        )

        if self.text:

            text_surface = self.font.render(
                self.text,
                True,
                (235, 235, 235),
            )

            text_rect = text_surface.get_rect(
                center=rect.center
            )

            surface.blit(
                text_surface,
                text_rect,
            )