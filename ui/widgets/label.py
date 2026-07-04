"""
label.py
========

Text rendering widget.

Labels display text anywhere in the UI.

Supports:

    • Alignment
    • Color
    • Font
    • Dynamic text
    • Cached rendering
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

import pygame

from .widget import Widget
from ui.renderer.layers import RenderLayer


class TextAlign(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class Label(Widget):
    """
    Basic text widget.
    """

    def __init__(
        self,
        text: str = "",
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        *,
        font: Optional[pygame.font.Font] = None,
        font_size: int = 24,
        color=(255, 255, 255),
        align: TextAlign = TextAlign.LEFT,
        layer: RenderLayer = RenderLayer.UI,
    ) -> None:

        super().__init__(
            x,
            y,
            width,
            height,
            layer=layer,
        )

        self._text = text

        self.font = (
            font
            if font is not None
            else pygame.font.SysFont(
                "arial",
                font_size,
            )
        )

        self.color = color

        self.align = align

        self._surface: Optional[pygame.Surface] = None

        self._dirty = True

    # ---------------------------------------------------------
    # Text
    # ---------------------------------------------------------

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(
        self,
        value: str,
    ) -> None:

        if value == self._text:
            return

        self._text = value

        self._dirty = True

    # ---------------------------------------------------------
    # Appearance
    # ---------------------------------------------------------

    def set_color(
        self,
        color,
    ) -> None:

        self.color = color
        self._dirty = True

    def set_font(
        self,
        font: pygame.font.Font,
    ) -> None:

        self.font = font
        self._dirty = True

    # ---------------------------------------------------------
    # Cache
    # ---------------------------------------------------------

    def _rebuild(self) -> None:

        self._surface = self.font.render(
            self._text,
            True,
            self.color,
        )

        self._dirty = False

    # ---------------------------------------------------------
    # Drawing
    # ---------------------------------------------------------

    def draw(
        self,
        surface: pygame.Surface,
    ) -> None:

        if self._dirty or self._surface is None:
            self._rebuild()

        if self._surface is None:
            return

        text_rect = self._surface.get_rect()

        rect = self.global_rect

        if self.align == TextAlign.LEFT:

            text_rect.midleft = (
                rect.left,
                rect.centery,
            )

        elif self.align == TextAlign.CENTER:

            text_rect.center = rect.center

        else:

            text_rect.midright = (
                rect.right,
                rect.centery,
            )

        surface.blit(
            self._surface,
            text_rect,
        )

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    @property
    def text_size(self):

        if self._dirty or self._surface is None:
            self._rebuild()

        return self._surface.get_size()

    def __repr__(self):

        return (
            f"Label("
            f"text='{self.text}', "
            f"x={self.x}, "
            f"y={self.y})"
        )