from __future__ import annotations

import pygame

from ui.screen import Screen
from ui import config

from ui.backgrounds import (
    StarField,
    GodStars,
    Dust,
    Fog,
)

from ui.effects.black_hole import BlackHole
from ui.effects.orbit_system import OrbitSystem
from ui.effects.falling_pieces import FallingSystem


class MainMenuScreen(Screen):
    """
    Production Main Menu.

    This screen acts as the coordinator for all visual
    systems. Rendering and animation logic remain inside
    the individual systems themselves.
    """

    def __init__(self, screen_size: tuple[int, int]):

        super().__init__()

        self.width, self.height = screen_size

        # -------------------------------------------------
        # Background Layers
        # -------------------------------------------------

        self.star_field = StarField(
            self.width,
            self.height,
        )

        self.god_stars = GodStars(
            self.width,
            self.height,
        )

        self.dust = Dust(
            self.width,
            self.height,
        )

        self.fog = Fog(
            self.width,
            self.height,
        )

        self.background_layers = (
            self.star_field,
            self.god_stars,
            self.dust,
            self.fog,
        )

        # -------------------------------------------------
        # Centerpiece
        # -------------------------------------------------

        hole_position = (
            int(self.width * 0.73),
            int(self.height * 0.50),
        )

        self.black_hole = BlackHole(
            hole_position
        )

        self.orbits = OrbitSystem(
            self.black_hole.position
        )

        self.falling = FallingSystem(
            self.width,
            self.height,
        )

        # -------------------------------------------------
        # UI
        # -------------------------------------------------

        self.title = None

        self.menu_panel = None

        self.buttons = []

        # -------------------------------------------------
        # Animation
        # -------------------------------------------------

        self.elapsed = 0.0

    # -----------------------------------------------------

    def on_enter(self):

        """Called when the screen becomes active."""

    # -----------------------------------------------------

    def on_exit(self):

        """Called before leaving the screen."""

    # -----------------------------------------------------

    def resize(
        self,
        width: int,
        height: int,
    ):

        self.width = width
        self.height = height

        for layer in self.background_layers:
            layer.resize(width, height)

        self.falling.resize(
            width,
            height,
        )

        self.black_hole.set_center(
            (
                int(width * 0.73),
                int(height * 0.50),
            )
        )

        self.orbits.set_center(
            self.black_hole.position
        )

    # -----------------------------------------------------

    def update(
        self,
        dt: float,
    ):

        self.elapsed += dt

        for layer in self.background_layers:
            layer.update(dt)

        self.black_hole.update(dt)

        self.orbits.update(dt)

        self.falling.update(dt)

    # -----------------------------------------------------

    def draw(
        self,
        surface: pygame.Surface,
    ):

        #
        # Background
        #

        for layer in self.background_layers:
            layer.draw(surface)

        #
        # World Effects
        #

        self.orbits.draw(surface)

        self.black_hole.draw(surface)

        self.falling.draw(surface)

        #
        # Widgets
        #
        # Implemented in Part-8C

    # -----------------------------------------------------

    def handle_event(
        self,
        event: pygame.event.Event,
    ):

        if event.type == pygame.VIDEORESIZE:

            self.resize(
                event.w,
                event.h,
            )
    
    @property
    def center(self):

        return (
            self.width // 2,
            self.height // 2,
        )


    @property
    def black_hole_center(self):

        return self.black_hole.position