from __future__ import annotations

import sys

import pygame

from ui import config
from ui.renderer.renderer import Renderer
from ui.screen_manager import ScreenManager
from ui.screens.main_menu import MainMenuScreen


class UIApplication:
    """
    Root UI application.

    Responsibilities
    ----------------
    • Initialize pygame
    • Own the application window
    • Own the renderer
    • Own the ScreenManager
    • Drive the main loop
    • Dispatch events
    • Handle resize
    • Present the rendered frame

    All screen-specific behaviour lives inside Screen classes.
    """

    def __init__(self) -> None:

        pygame.init()

        pygame.display.set_caption(config.WINDOW_TITLE)

        self.window = pygame.display.set_mode(
            (
                config.WINDOW_WIDTH,
                config.WINDOW_HEIGHT,
            ),
            pygame.RESIZABLE,
        )

        self.clock = pygame.time.Clock()

        self.running = False

        #
        # Rendering
        #

        self.renderer = Renderer()

        #
        # Screen System
        #

        self.screen_manager = ScreenManager(
            self.window
        )

        self._register_screens()

    # ---------------------------------------------------------
    # Screen Registration
    # ---------------------------------------------------------

    def _register_screens(self) -> None:
        """
        Register the initial screen.

        Future screens (Difficulty, Settings,
        Campaign Map, Battle UI, etc.) will
        also be created here.
        """

        self.screen_manager.replace(
            MainMenuScreen(
                self.screen_manager
            )
        )

    # ---------------------------------------------------------
    # Main Loop
    # ---------------------------------------------------------

    def run(self) -> None:

        self.running = True

        while self.running:

            dt = (
                self.clock.tick(
                    config.TARGET_FPS
                )
                / 1000.0
            )

            self._process_events()

            self._update(dt)

            self._render()

        pygame.quit()

    # ---------------------------------------------------------
    # Events
    # ---------------------------------------------------------

    def _process_events(self) -> None:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

                return

            if event.type == pygame.VIDEORESIZE:

                self.window = pygame.display.set_mode(
                    (
                        event.w,
                        event.h,
                    ),
                    pygame.RESIZABLE,
                )

                #
                # Keep ScreenManager synchronized
                #

                self.screen_manager.window = self.window

                self.screen_manager.resize(
                    (
                        event.w,
                        event.h,
                    )
                )

            self.screen_manager.handle_event(
                event
            )

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def _update(
        self,
        dt: float,
    ) -> None:

        self.screen_manager.update(dt)

    # ---------------------------------------------------------
    # Render
    # ---------------------------------------------------------

    def _render(self) -> None:

        #
        # Clear window
        #

        self.window.fill(
            config.BACKGROUND_COLOR
        )

        #
        # Begin renderer frame.
        #
        # The renderer will become responsible
        # for layered rendering during later UI
        # phases.
        #

        self.renderer.begin_frame()

        #
        # Draw current screen
        #

        self.screen_manager.draw()

        #
        # Render queued objects
        #
        # (Currently empty because the renderer
        # is being introduced before the UI is
        # migrated to queued rendering.)
        #

        self.renderer.render(
            self.window
        )

        pygame.display.flip()

    # ---------------------------------------------------------

    def stop(self) -> None:

        self.running = False


def run() -> None:
    """
    Launch the production UI.
    """

    UIApplication().run()


if __name__ == "__main__":
    run()