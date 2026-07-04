"""
Global UI configuration.

This module contains tweakable values used throughout the UI.
Keeping them here avoids scattering "magic numbers" across the codebase.
"""

# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

TARGET_FPS = 60

# ---------------------------------------------------------
# Background
# ---------------------------------------------------------

STAR_COUNT = 180
GOD_STAR_COUNT = 18

DUST_PARTICLE_COUNT = 80
FOG_LAYER_COUNT = 3

PARALLAX_STRENGTH = 0.15

# ---------------------------------------------------------
# Black Hole
# ---------------------------------------------------------

BLACK_HOLE_RADIUS = 135

BLACK_HOLE_PULSE_SPEED = 1.25
BLACK_HOLE_ROTATION_SPEED = 12.0

# ---------------------------------------------------------
# Orbiting Pieces
# ---------------------------------------------------------

ORBIT_PIECE_COUNT = 10

ORBIT_MIN_RADIUS = 180
ORBIT_MAX_RADIUS = 340

ORBIT_MIN_SPEED = 0.12
ORBIT_MAX_SPEED = 0.45

# ---------------------------------------------------------
# Falling Pieces
# ---------------------------------------------------------

FALLING_PIECE_COUNT = 12

FALL_SPEED_MIN = 30
FALL_SPEED_MAX = 120

# ---------------------------------------------------------
# Menu
# ---------------------------------------------------------

MENU_WIDTH = 420

MENU_BUTTON_SPACING = 20

MENU_ANIMATION_TIME = 0.45