from __future__ import annotations

import pygame
import random
from pathlib import Path

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
from ui.assets import Assets

from ui.resources.chess_cache import chess_piece_manager


class MainMenuScreen(Screen):
    """
    Production Main Menu.

    This screen acts as the coordinator for all visual
    systems. Rendering and animation logic remain inside
    the individual systems themselves.
    """

    def __init__(self, manager):

        super().__init__(manager)


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

        # Root widget hierarchy
        self.widgets = []

        self.menu_panel = None

        self.buttons = []

        #
        # UI assets
        #
        self.ui_frame = None

        #
        # All themed button skins.
        # Key = button name
        # Value = ButtonSkin
        #
        self.button_skins: dict[str, object] = {}

        self._load_ui_assets()

        self._build_ui()

        # -------------------------------------------------
        # Animation
        # -------------------------------------------------

        self.elapsed = 0.0

        #
        # Cached Assets
        #

        self.chess_pieces = self._load_chess_pieces()

        #
        # Validate that every themed piece
        # has been successfully loaded.
        #

        assert len(self.chess_pieces) == 12


    def on_first_enter(self):

        self._populate_orbits()

        self._populate_falling()

    # -----------------------------------------------------

    def enter(self):

        super().enter()

        self.elapsed = 0.0

    # -----------------------------------------------------
    
    def exit(self):

        super().exit()

    # -----------------------------------------------------

    def resize(
        self,
        size: tuple[int, int],
    ):

        super().resize(size)

        width, height = size

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

        if self.menu_panel:

            panel_width = 558
            panel_height = 447

            self.menu_panel.rect.x = 70
            self.menu_panel.rect.y = (
                self.height // 2 - panel_height // 2
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

        for widget in self.widgets:
            widget.update(dt)
    
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

        for widget in self.widgets:
            widget.render(surface)

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

            return

        for widget in reversed(self.widgets):
            widget.handle_event(event)
    
    @property
    def center(self):

        return (
            self.width // 2,
            self.height // 2,
        )


    @property
    def black_hole_center(self):

        return self.black_hole.position

    def _load_ui_assets(self):
        """
        Load all UI assets used by the main menu.

        This method is called once during screen
        initialization.
        """

        project_root = Path(__file__).resolve().parents[2]

        #
        # -------------------------------------------------
        # Frame
        # -------------------------------------------------
        #

        frame_path = (
            project_root
            / "Assets"
            / "Generated_assets"
            / "UI"
            / "Frame"
            / "frame.png"
        )

        self.ui_frame = Assets.texture(frame_path)

        #
        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------
        #

        button_names = (
            "play",
            "load_game",
            "settings",
            "exit",
        )

        button_root = (
            project_root
            / "Assets"
            / "Generated_assets"
            / "UI"
            / "Buttons"
        )

        for button_name in button_names:

            self.button_skins[button_name] = Assets.load_button_images(

                name=f"main_menu_{button_name}",

                idle=(
                    button_root
                    / "Idle"
                    / f"{button_name}.png"
                ),

                hover=(
                    button_root
                    / "Hover"
                    / f"{button_name}.png"
                ),

                pressed=(
                    button_root
                    / "Pressed"
                    / f"{button_name}.png"
                ),
            )


    def _build_ui(self):
        """
        Construct the widget hierarchy.

        Visual styling remains inside the widget classes.
        This screen is only responsible for composition.
        """

        # Imported locally to avoid circular imports.
        from ui.widgets.panel import Panel
        from ui.widgets.button import Button

        #
        # Use the artwork aspect ratio.
        #
        panel_width = 558
        panel_height = 447

        self.menu_panel = Panel(
            x=70,
            y=self.height // 2 - panel_height // 2,
            width=panel_width,
            height=panel_height,
            background_image=self.ui_frame,
        )

        labels = (
            "Play",
            "Load Game",
            "Settings",
            "Exit",
        )

        #
        # Tuned for the new frame artwork.
        #

        button_width = 320
        button_height = 150

        start_y = 35
        spacing = 92

        self.buttons.clear()

        for index, text in enumerate(labels):

            #
            # Only the Play button is themed.
            #

            skin = self.button_skins.get(text.lower().replace(" ", "_"))

            button = Button(
                x=(panel_width - button_width) // 2,
                y=start_y + index * spacing,
                width=button_width,
                height=button_height,
                text="" if skin else text,
                skin=skin,
            )

            self.menu_panel.add_child(button)

            self.buttons.append(button)

        self.widgets = [self.menu_panel]


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

        colors = ("white", "black")
        names = ("king", "queen", "rook", "bishop", "knight", "pawn")

        assets = [
            (color, piece)
            for color in colors
            for piece in names
        ]

        random.shuffle(assets)

        for i in range(config.ORBIT_PIECE_COUNT):

            color, piece = assets[i % len(assets)]

            self.orbits.add(
                chess_piece_manager.get(color, piece),
                base_scale=chess_piece_manager.get_base_scale(piece),
            )

    def _populate_falling(self):

        self.falling.clear()

        colors = ("white", "black")
        names = ("king", "queen", "rook", "bishop", "knight", "pawn")

        assets = [
            (color, piece)
            for color in colors
            for piece in names
        ]

        for _ in range(config.FALLING_PIECE_COUNT):

            color, piece = random.choice(assets)

            self.falling.add(
                chess_piece_manager.get(color, piece),
                base_scale=chess_piece_manager.get_base_scale(piece),
            )

    def _piece_pool(self):

        pieces = self.chess_pieces.copy()

        random.shuffle(pieces)

        while True:

            for piece in pieces:
                yield piece

            random.shuffle(pieces)