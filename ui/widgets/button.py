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

        colors = {
            "idle": (70, 70, 70),
            "hover": (95, 95, 95),
            "pressed": (45, 45, 45),
            "disabled": (35, 35, 35),
        }

        rect = self.global_rect

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