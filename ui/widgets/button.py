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
- Future keyboard focus support
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

    Rendering is intentionally generic. Visual styling comes from
    subclasses or sprite-sheet skins.
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

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        """
        Returns current visual state.

        disabled
        pressed
        hover
        idle
        """

        if not self.enabled:
            return "disabled"

        if self.pressed:
            return "pressed"

        if self.hovered:
            return "hover"

        return "idle"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Returns True if the event was consumed.
        """

        if not self.enabled or not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.hovered

            self.hovered = self.rect.collidepoint(event.pos)

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

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self.animator.update(dt)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """
        Placeholder rendering.

        Production rendering will use button sprite sheets.
        """

        if not self.visible:
            return

        colors = {
            "idle": (70, 70, 70),
            "hover": (95, 95, 95),
            "pressed": (45, 45, 45),
            "disabled": (35, 35, 35),
        }

        pygame.draw.rect(
            surface,
            colors[self.state],
            self.rect,
            border_radius=8,
        )

        pygame.draw.rect(
            surface,
            (180, 180, 180),
            self.rect,
            width=2,
            border_radius=8,
        )