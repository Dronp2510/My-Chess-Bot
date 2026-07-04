"""
image.py

Generic image widget used throughout the UI framework.

Supports:
- Scaling
- Rotation
- Opacity
- Visibility
- Anchor positioning
- Future animation integration
"""

from __future__ import annotations

from typing import Optional

import pygame

from .widget import Widget
from ui.animation.animator import Animator


class Image(Widget):
    """
    Generic image widget.

    Used for backgrounds, icons, artwork, decorative UI,
    portraits, chess pieces, and render textures.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        image: Optional[pygame.Surface] = None,
        visible: bool = True,
    ) -> None:
        super().__init__(rect)

        self.image = image
        self.visible = visible

        self.scale = 1.0
        self.rotation = 0.0
        self.opacity = 255

        self.anchor = "center"

        self.animator = Animator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_image(self, image: Optional[pygame.Surface]) -> None:
        self.image = image

    def set_scale(self, scale: float) -> None:
        self.scale = max(0.01, scale)

    def set_rotation(self, angle: float) -> None:
        self.rotation = angle % 360

    def set_opacity(self, opacity: int) -> None:
        self.opacity = max(0, min(255, opacity))

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self.animator.update(dt)

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _get_transformed_image(self) -> Optional[pygame.Surface]:
        """
        Applies scaling, rotation and opacity.

        Returns
        -------
        pygame.Surface | None
        """

        if self.image is None:
            return None

        image = self.image

        # Scale
        if self.scale != 1.0:
            width = max(1, int(image.get_width() * self.scale))
            height = max(1, int(image.get_height() * self.scale))

            image = pygame.transform.smoothscale(
                image,
                (width, height),
            )

        # Rotation
        if self.rotation != 0:
            image = pygame.transform.rotate(
                image,
                self.rotation,
            )

        # Opacity
        if self.opacity != 255:
            image = image.copy()
            image.set_alpha(self.opacity)

        return image

    def _get_draw_rect(
        self,
        image: pygame.Surface,
    ) -> pygame.Rect:
        """
        Returns the destination rectangle based on
        the current anchor.
        """

        rect = image.get_rect()

        match self.anchor:
            case "topleft":
                rect.topleft = self.rect.topleft

            case "topright":
                rect.topright = self.rect.topright

            case "bottomleft":
                rect.bottomleft = self.rect.bottomleft

            case "bottomright":
                rect.bottomright = self.rect.bottomright

            case "midtop":
                rect.midtop = self.rect.midtop

            case "midbottom":
                rect.midbottom = self.rect.midbottom

            case "midleft":
                rect.midleft = self.rect.midleft

            case "midright":
                rect.midright = self.rect.midright

            case _:
                rect.center = self.rect.center

        return rect

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        image = self._get_transformed_image()

        if image is None:
            return

        draw_rect = self._get_draw_rect(image)

        surface.blit(image, draw_rect)