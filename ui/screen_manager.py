from __future__ import annotations

from typing import List, Optional

import pygame

from ui.screen import Screen


class ScreenManager:
    """
    Owns every UI screen.

    Uses a stack architecture.

    Example

        Main Menu

            ↓ push

        Difficulty

            ↓ push

        Inventory

            ↓ pop

        Difficulty

            ↓ replace

        Map
    """

    def __init__(self, window: pygame.Surface):

        self.window = window
        self.window_size = window.get_size()

        self._stack: List[Screen] = []

    # ---------------------------------------------------------
    # Stack
    # ---------------------------------------------------------

    def push(self, screen: Screen) -> None:
        """
        Push a new screen.

        Previous screen remains underneath.
        """

        if self.current is not None:
            self.current.exit()

        self._stack.append(screen)

        screen.enter()

    def pop(self) -> Optional[Screen]:
        """
        Remove top screen.
        """

        if not self._stack:
            return None

        old = self._stack.pop()

        old.exit()

        if self.current is not None:
            self.current.enter()

        return old

    def replace(self, screen: Screen) -> None:
        """
        Replace current screen.
        """

        self.clear()

        self.push(screen)

    def clear(self) -> None:

        while self._stack:
            self._stack.pop().exit()

    # ---------------------------------------------------------
    # Runtime
    # ---------------------------------------------------------

    def update(self, dt: float) -> None:

        if self.current:
            self.current.update(dt)

    def draw(self) -> None:

        if self.current:
            self.current.draw(self.window)

    def handle_event(self, event: pygame.event.Event) -> None:

        if self.current:
            self.current.handle_event(event)

    # ---------------------------------------------------------
    # Resize
    # ---------------------------------------------------------

    def resize(self, size: tuple[int, int]) -> None:

        self.window_size = size

        for screen in self._stack:
            screen.resize(size)

    # ---------------------------------------------------------

    @property
    def current(self) -> Optional[Screen]:

        if not self._stack:
            return None

        return self._stack[-1]

    @property
    def stack_depth(self) -> int:

        return len(self._stack)

    @property
    def is_empty(self) -> bool:

        return len(self._stack) == 0