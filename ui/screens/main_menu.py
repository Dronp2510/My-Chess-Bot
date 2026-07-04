from __future__ import annotations

import pygame
import random

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

from ui.resources.chess_cache import chess_piece_manager


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

        #
        # Cached Assets
        #

        self.chess_pieces = self._load_chess_pieces()

        #
        # Populate systems
        #

        self._populate_orbits()

        self._populate_falling()

    # -----------------------------------------------------

    def on_enter(self):

        """Called when the screen becomes active."""
        self.elapsed = 0.0

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

        self._populate_falling()

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


    def _load_chess_pieces(self) -> list[pygame.Surface]:
        """
        Load all chess pieces once.

        The returned list is reused by the orbit and
        falling systems.
        """

        pieces = []

        colors = (
            "white",
            "black",
        )

        names = (
            "king",
            "queen",
            "rook",
            "bishop",
            "knight",
            "pawn",
        )

        for color in colors:
            for piece in names:
                pieces.append(
                    chess_piece_manager.get(
                        color,
                        piece,
                    )
                )

        return pieces
    

    def _populate_orbits(self):

        self.orbits.clear()

        for _ in range(config.ORBIT_PIECE_COUNT):

            pool = self._piece_pool()

            sprite = next(pool)

            self.orbits.add(sprite)


    def _populate_falling(self):

        self.falling.clear()

        for _ in range(config.FALLING_PIECE_COUNT):

            sprite = random.choice(
                self.chess_pieces
            )

            self.falling.add(sprite)

    def _piece_pool(self):

        pieces = self.chess_pieces.copy()

        random.shuffle(pieces)

        while True:

            for piece in pieces:
                yield piece

            random.shuffle(pieces)