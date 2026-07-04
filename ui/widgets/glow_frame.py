"""
glow_frame.py

Reusable glowing frame widget.

Provides an animated border that can be attached to
other widgets to indicate selection, hover, focus,
or special effects.

Features
--------
- Adjustable glow intensity
- Adjustable border width
- Rounded corners
- Optional pulsing
- Opacity control
- Theme-friendly
"""

from __future__ import annotations

import math

import pygame

from .widget import Widget
from ui.animation.animator import Animator


class GlowFrame(Widget):
    """
    Animated glowing border widget.

    Intended to be rendered above or below another widget.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        *,
        color: tuple[int, int, int] = (180, 120, 255),
        border_width: int = 3,
        glow_size: int = 12,
        corner_radius: int = 10,
        opacity: int = 180,
        pulse: bool = False,
        pulse_speed: float = 2.0,
        visible: bool = True,
    ) -> None:
        super().__init__(rect)

        self.color = color

        self.border_width = border_width
        self.glow_size = glow_size
        self.corner_radius = corner_radius

        self.opacity = opacity

        self.visible = visible

        self.pulse = pulse
        self.pulse_speed = pulse_speed

        self.animator = Animator()

        self._time = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def set_color(
        self,
        color: tuple[int, int, int],
    ) -> None:
        self.color = color

    def set_opacity(
        self,
        opacity: int,
    ) -> None:
        self.opacity = max(0, min(255, opacity))

    def set_glow_size(
        self,
        size: int,
    ) -> None:
        self.glow_size = max(0, size)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self.animator.update(dt)
        self._time += dt

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        alpha = self.opacity

        if self.pulse:
            alpha = int(
                self.opacity
                * (
                    0.75
                    + 0.25
                    * (
                        math.sin(
                            self._time * self.pulse_speed * math.pi * 2
                        )
                        + 1
                    )
                )
            )

        padding = self.glow_size

        glow_rect = self.rect.inflate(
            padding * 2,
            padding * 2,
        )

        glow_surface = pygame.Surface(
            glow_rect.size,
            pygame.SRCALPHA,
        )

        # --------------------------------------------------------------
        # Fake glow using expanding translucent outlines
        # --------------------------------------------------------------

        steps = max(1, self.glow_size)

        for i in range(steps, 0, -1):

            a = int(alpha * (i / (steps * 4)))

            pygame.draw.rect(
                glow_surface,
                (*self.color, a),
                pygame.Rect(
                    steps - i,
                    steps - i,
                    glow_rect.width - (steps - i) * 2,
                    glow_rect.height - (steps - i) * 2,
                ),
                width=self.border_width,
                border_radius=self.corner_radius + i,
            )

        # Main border
        pygame.draw.rect(
            glow_surface,
            (*self.color, alpha),
            pygame.Rect(
                steps,
                steps,
                self.rect.width,
                self.rect.height,
            ),
            width=self.border_width,
            border_radius=self.corner_radius,
        )

        surface.blit(
            glow_surface,
            (
                self.rect.x - padding,
                self.rect.y - padding,
            ),
        )