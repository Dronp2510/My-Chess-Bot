"""
icon_button.py

Button widget capable of displaying an icon alongside optional text.

Inherits all interaction behaviour from Button.
"""

from __future__ import annotations

from typing import Optional

import pygame

from .button import Button


class IconButton(Button):
    """
    Button that displays an icon.

    The icon may be centered or aligned to the left depending on
    whether text is present.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        icon: Optional[pygame.Surface] = None,
        text: str = "",
        icon_padding: int = 12,
        icon_scale: float = 1.0,
        **kwargs,
    ) -> None:
        super().__init__(rect, text=text, **kwargs)

        self.icon = icon
        self.icon_padding = icon_padding
        self.icon_scale = icon_scale

        self.icon_tint = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_icon(self, icon: Optional[pygame.Surface]) -> None:
        self.icon = icon

    def set_icon_scale(self, scale: float) -> None:
        self.icon_scale = max(0.1, scale)

    def set_icon_tint(
        self,
        color: Optional[tuple[int, int, int]],
    ) -> None:
        """
        Reserved for future theme support.
        """
        self.icon_tint = color

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the button followed by its icon.

        Future sprite-sheet rendering will replace the base draw()
        without affecting icon rendering.
        """

        super().draw(surface)

        if not self.visible:
            return

        if self.icon is None:
            return

        icon = self.icon

        if self.icon_scale != 1.0:
            size = (
                int(icon.get_width() * self.icon_scale),
                int(icon.get_height() * self.icon_scale),
            )

            icon = pygame.transform.smoothscale(icon, size)

        icon_rect = icon.get_rect()

        # --------------------------------------------------------------
        # Layout
        # --------------------------------------------------------------

        if self.text:
            icon_rect.centery = self.rect.centery
            icon_rect.left = self.rect.left + self.icon_padding
        else:
            icon_rect.center = self.rect.center

        # --------------------------------------------------------------
        # Future tint support
        # --------------------------------------------------------------

        if self.icon_tint is not None:
            tinted = icon.copy()
            tinted.fill(
                self.icon_tint,
                special_flags=pygame.BLEND_RGBA_MULT,
            )
            icon = tinted

        surface.blit(icon, icon_rect)