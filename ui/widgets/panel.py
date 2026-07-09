"""
panel.py
========

Basic rectangular panel widget.

Panels are the primary container widgets of the UI framework.

They can optionally draw:

    • Background
    • Border
    • Rounded corners

Panels also act as parent containers for other widgets.
"""

from __future__ import annotations

from typing import Optional

import pygame

from .widget import Widget
from ui.renderer.layers import RenderLayer


class Panel(Widget):
    """
    Basic rectangular UI panel.
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 100,
        *,
        background_color=(40, 40, 45),
        border_color=(180, 180, 180),
        border_width: int = 2,
        border_radius: int = 8,
        background_image: pygame.Surface | None = None,
        layer: RenderLayer = RenderLayer.UI,
    ) -> None:

        super().__init__(
            x,
            y,
            width,
            height,
            layer=layer,
        )

        self.background_color = background_color

        self.border_color = border_color

        self.border_width = border_width

        self.border_radius = border_radius

        self.surface: Optional[pygame.Surface] = None

        #
        # Optional themed frame image.
        #
        self.background_image = background_image

        #
        # Cached scaled frame.
        #
        self._scaled_background: Optional[pygame.Surface] = None

        #
        # Size used for cached scaling.
        #
        self._cached_background_size = (width, height)

        self._dirty = True

    # ---------------------------------------------------------
    # Cache
    # ---------------------------------------------------------

    def invalidate(self) -> None:
        """
        Marks the cached panel surface for rebuilding.
        """

        self._dirty = True

    def set_background_image(
        self,
        image: pygame.Surface | None,
    ) -> None:
        """
        Assign or remove a themed panel image.
        """

        self.background_image = image

        self._scaled_background = None

        self.invalidate()

    def _rebuild_background_cache(self) -> None:
        """
        Rebuilds the scaled frame image.
        """

        if self.background_image is None:
            return

        self._scaled_background = pygame.transform.smoothscale(
            self.background_image,
            (self.width, self.height),
        )

        self._cached_background_size = (
            self.width,
            self.height,
        )

    def _rebuild_surface(self) -> None:
        """
        Rebuilds the cached panel surface.
        """

        #
        # Resize changed?
        #

        if (
            self.background_image is not None
            and (
                self._scaled_background is None
                or self._cached_background_size != (
                    self.width,
                    self.height,
                )
            )
        ):
            self._rebuild_background_cache()
        
        if self.width <= 0 or self.height <= 0:
            return

        self.surface = pygame.Surface(
            self.rect.size,
            pygame.SRCALPHA,
        )

        self.surface.fill((0, 0, 0, 0))

        pygame.draw.rect(
            self.surface,
            self.background_color,
            self.surface.get_rect(),
            border_radius=self.border_radius,
        )

        if self.border_width > 0:

            pygame.draw.rect(
                self.surface,
                self.border_color,
                self.surface.get_rect(),
                width=self.border_width,
                border_radius=self.border_radius,
            )

        self._dirty = False

    # ---------------------------------------------------------
    # Drawing
    # ---------------------------------------------------------

    def draw(
        self,
        surface: pygame.Surface,
    ) -> None:

        #
        # -----------------------------------------------------
        # Themed Panel Rendering
        # -----------------------------------------------------
        #

        if self.background_image is not None:

            #
            # Panel resized?
            #

            if (
                self._scaled_background is None
                or self._cached_background_size != (
                    self.width,
                    self.height,
                )
            ):
                self._rebuild_background_cache()

            if self._scaled_background is not None:

                surface.blit(
                    self._scaled_background,
                    self.global_position,
                )

            return

        #
        # -----------------------------------------------------
        # Fallback Rendering
        # (Current placeholder implementation)
        # -----------------------------------------------------
        #

        if self._dirty or self.surface is None:
            self._rebuild_surface()

        if self.surface is None:
            return

        surface.blit(
            self.surface,
            self.global_position,
        )

    # ---------------------------------------------------------
    # Appearance
    # ---------------------------------------------------------

    def set_background_color(
        self,
        color,
    ) -> None:

        self.background_color = color
        self.invalidate()

    def set_border_color(
        self,
        color,
    ) -> None:

        self.border_color = color
        self.invalidate()

    def set_border_width(
        self,
        width: int,
    ) -> None:

        self.border_width = width
        self.invalidate()

    def set_border_radius(
        self,
        radius: int,
    ) -> None:

        self.border_radius = radius
        self.invalidate()

    # ---------------------------------------------------------
    # Size
    # ---------------------------------------------------------

    def resize(
        self,
        width: int,
        height: int,
    ) -> None:

        self.size = (width, height)

        self.invalidate()

    # ---------------------------------------------------------
    # Debug
    # ---------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"Panel("
            f"x={self.x}, "
            f"y={self.y}, "
            f"w={self.width}, "
            f"h={self.height})"
        )