"""
layers.py
=========

Defines the global rendering order used throughout
the War Chess UI framework.

Lower layer values are rendered first.

Higher layer values are rendered later and therefore
appear above lower layers.

This ordering is shared by every screen in the game.

Examples
--------
BACKGROUND
    Space background
    Campaign backgrounds
    Battle backgrounds

PARTICLES_BACK
    Dust
    Fog
    Stars

WORLD
    Chess board
    Campaign map
    Large world objects

PIECES
    Chess pieces

EFFECTS
    Ability effects
    Highlights
    Glows

UI
    Panels
    Buttons
    Windows

TOOLTIPS
    Hover information

OVERLAY
    Fade effects
    Screen transitions
"""

from enum import IntEnum


class RenderLayer(IntEnum):
    """
    Global rendering order.

    Lower numbers render first.
    """

    # ---------------------------------------------------------
    # Background
    # ---------------------------------------------------------

    BACKGROUND = 0

    # Large atmospheric particles
    PARTICLES_BACK = 10

    # ---------------------------------------------------------
    # World
    # ---------------------------------------------------------

    WORLD = 20

    # Chess pieces / characters
    PIECES = 30

    # Front particles
    PARTICLES_FRONT = 40

    # Ability effects
    EFFECTS = 50

    # Selection
    HIGHLIGHTS = 60

    # ---------------------------------------------------------
    # User Interface
    # ---------------------------------------------------------

    UI = 70

    # Floating widgets
    POPUPS = 80

    # Tooltips
    TOOLTIPS = 90

    # Cursor
    CURSOR = 100

    # Fade / transitions
    OVERLAY = 110

    # Debug rendering
    DEBUG = 120