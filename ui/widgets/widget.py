"""
widget.py
=========

Base widget class for the War Chess UI framework.

Every visible UI component inherits from Widget.

Responsibilities
----------------
• Position & Size
• Visibility
• Enable / Disable
• Parent / Child hierarchy
• Rendering
• Updating
• Event propagation
• Animation registration
"""

from __future__ import annotations

from typing import List, Optional

import pygame

from ui.animation import Animator
from ui.renderer.layers import RenderLayer
from ui.renderer.renderable import Renderable


class Widget(Renderable):
    """
    Base class for every UI widget.
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        *,
        layer: RenderLayer = RenderLayer.UI,
    ) -> None:

        super().__init__(layer)

        self.rect = pygame.Rect(x, y, width, height)

        self.parent: Optional["Widget"] = None
        self.children: List["Widget"] = []

        self.visible = True
        self.enabled = True

        self.animator = Animator()

        self.opacity = 255
        self.scale = 1.0
        self.rotation = 0.0

        self.name = self.__class__.__name__

    # ======================================================
    # Position
    # ======================================================

    @property
    def x(self) -> int:
        return self.rect.x

    @x.setter
    def x(self, value: int) -> None:
        self.rect.x = value

    @property
    def y(self) -> int:
        return self.rect.y

    @y.setter
    def y(self, value: int) -> None:
        self.rect.y = value

    @property
    def width(self) -> int:
        return self.rect.width

    @width.setter
    def width(self, value: int) -> None:
        self.rect.width = value

    @property
    def height(self) -> int:
        return self.rect.height

    @height.setter
    def height(self, value: int) -> None:
        self.rect.height = value

    @property
    def position(self) -> tuple[int, int]:
        return self.rect.topleft

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        self.rect.topleft = value

    @property
    def size(self) -> tuple[int, int]:
        return self.rect.size

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        self.rect.size = value

    # ======================================================
    # Global Geometry
    # ======================================================

    @property
    def global_position(self) -> tuple[int, int]:

        if self.parent is None:
            return self.rect.topleft

        px, py = self.parent.global_position

        return (
            px + self.rect.x,
            py + self.rect.y,
        )

    @property
    def global_rect(self) -> pygame.Rect:

        rect = self.rect.copy()
        rect.topleft = self.global_position

        return rect

    # ======================================================
    # Hierarchy
    # ======================================================

    def add_child(self, widget: "Widget") -> None:

        if widget.parent is self:
            return

        if widget.parent is not None:
            widget.parent.remove_child(widget)

        widget.parent = self

        self.children.append(widget)

    def remove_child(self, widget: "Widget") -> None:

        if widget in self.children:
            self.children.remove(widget)
            widget.parent = None

    def clear_children(self) -> None:

        for child in self.children:
            child.parent = None

        self.children.clear()

    # ======================================================
    # Visibility
    # ======================================================

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    # ======================================================
    # Enable
    # ======================================================

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    # ======================================================
    # Update
    # ======================================================

    def update(self, dt: float) -> None:

        if not self.visible:
            return

        self.animator.update(dt)

        self.on_update(dt)

        for child in self.children:
            child.update(dt)

    # ======================================================
    # Event Handling
    # ======================================================

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> bool:

        if not self.visible or not self.enabled:
            return False

        for child in reversed(self.children):

            if child.handle_event(event):
                return True

        return False

    # ======================================================
    # Rendering
    # ======================================================

    def render(
        self,
        surface: pygame.Surface,
    ) -> None:

        if not self.visible:
            return

        self.draw(surface)

        for child in self.children:
            child.render(surface)

    # ======================================================
    # Animation
    # ======================================================

    def animate(self, animation):

        return self.animator.add(animation)

    def clear_animations(self) -> None:

        self.animator.clear()

    # ======================================================
    # Hooks
    # ======================================================

    def on_update(self, dt: float) -> None:
        pass

    def on_mouse_enter(self) -> None:
        pass

    def on_mouse_exit(self) -> None:
        pass

    def on_mouse_down(self, button: int) -> None:
        pass

    def on_mouse_up(self, button: int) -> None:
        pass

    def on_click(self) -> None:
        pass

    # ======================================================
    # Drawing
    # ======================================================

    def draw(
        self,
        surface: pygame.Surface,
    ) -> None:
        pass

    # ======================================================
    # Utility
    # ======================================================

    def contains_point(
        self,
        position: tuple[int, int],
    ) -> bool:

        return self.global_rect.collidepoint(position)

    def move(
        self,
        dx: int,
        dy: int,
    ) -> None:

        self.rect.move_ip(dx, dy)

    def center_on(
        self,
        rect: pygame.Rect,
    ) -> None:

        self.rect.center = rect.center

    def __repr__(self) -> str:

        return (
            f"{self.name}("
            f"x={self.x}, "
            f"y={self.y}, "
            f"w={self.width}, "
            f"h={self.height})"
        )