from __future__ import annotations

from abc import ABC
from typing import Optional

import pygame


class Screen(ABC):
    """
    Base class for every UI screen.

    Lifecycle:

        enter()
            ↓
        update()
        handle_event()
        draw()
            ↓
        exit()

    Every screen in the project inherits from this class.
    """

    def __init__(self, manager: "ScreenManager") -> None:
        self.manager = manager
        self.window_size = manager.window_size

        self.initialized = False
        self.active = False

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def enter(self) -> None:
        """
        Called exactly once whenever the screen becomes active.
        """
        self.active = True

        if not self.initialized:
            self.on_first_enter()
            self.initialized = True

    def exit(self) -> None:
        """
        Called immediately before the screen is removed or hidden.
        """
        self.active = False

    def on_first_enter(self) -> None:
        """
        Called only the first time this screen is entered.

        Override if assets need pre-processing,
        procedural generation, etc.
        """

    # ---------------------------------------------------------
    # Runtime
    # ---------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Update animations and logic.
        """

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the entire screen.
        """

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events.
        """

    # ---------------------------------------------------------
    # Resize
    # ---------------------------------------------------------

    def resize(self, size: tuple[int, int]) -> None:
        """
        Window resized.
        """

        self.window_size = size

    # ---------------------------------------------------------

    @property
    def width(self) -> int:
        return self.window_size[0]

    @property
    def height(self) -> int:
        return self.window_size[1]