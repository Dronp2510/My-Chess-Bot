from __future__ import annotations

import math

import pygame

from ui import config


class BlackHole:
    """
    Animated cosmic black hole.

    Responsible for:

    • Event horizon
    • Accretion ring
    • Ambient glow
    • Rotation
    • Pulse

    Future versions may add:

    • Distortion shader
    • Particles
    • Gravitational lensing
    """

    def __init__(
        self,
        center: tuple[int, int],
        radius: float = config.BLACK_HOLE_RADIUS,
    ):

        self.center = pygame.Vector2(center)

        self.base_radius = radius

        self.rotation = 0.0

        self.time = 0.0

    # -----------------------------------------------------

    @property
    def pulse(self):

        return (
            math.sin(
                self.time
                * config.BLACK_HOLE_PULSE_SPEED
            )
            * 0.5
            + 0.5
        )

    # -----------------------------------------------------

    @property
    def radius(self):

        return self.base_radius * (
            0.96 + self.pulse * 0.08
        )

    # -----------------------------------------------------

    def set_center(self, center):

        self.center.update(center)

    # -----------------------------------------------------

    def update(self, dt):

        self.time += dt

        self.rotation += (
            config.BLACK_HOLE_ROTATION_SPEED
            * dt
        )

        self.rotation %= 360

    # -----------------------------------------------------

    def draw(self, surface):

        cx = int(self.center.x)
        cy = int(self.center.y)

        radius = self.radius

        #
        # Outer Glow
        #

        glow_radius = radius * 2.3

        glow = pygame.Surface(
            (
                int(glow_radius * 2),
                int(glow_radius * 2),
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow,
            (90, 40, 170, 25),
            (
                int(glow_radius),
                int(glow_radius),
            ),
            int(glow_radius),
        )

        pygame.draw.circle(
            glow,
            (150, 70, 220, 18),
            (
                int(glow_radius),
                int(glow_radius),
            ),
            int(glow_radius * 0.72),
        )

        surface.blit(
            glow,
            (
                cx - glow_radius,
                cy - glow_radius,
            ),
        )

        #
        # Accretion Ring
        #

        ring_surface = pygame.Surface(
            (
                int(radius * 4),
                int(radius * 4),
            ),
            pygame.SRCALPHA,
        )

        center = (
            int(radius * 2),
            int(radius * 2),
        )

        for angle in range(0, 360, 10):

            theta = math.radians(
                angle + self.rotation
            )

            orbit = radius * (
                1.15
                + 0.08
                * math.sin(
                    theta * 4
                    + self.time
                )
            )

            x = center[0] + orbit * math.cos(theta)
            y = center[1] + orbit * math.sin(theta)

            pygame.draw.circle(

                ring_surface,

                (170, 110, 255, 130),

                (int(x), int(y)),

                4,

            )

        surface.blit(
            ring_surface,
            (
                cx - radius * 2,
                cy - radius * 2,
            ),
        )

        #
        # Event Horizon
        #

        pygame.draw.circle(

            surface,

            (22, 18, 28),

            (cx, cy),

            int(radius),

        )

        #
        # Inner Void
        #

        pygame.draw.circle(

            surface,

            (0, 0, 0),

            (cx, cy),

            int(radius * 0.83),

        )

    @property
    def position(self) -> pygame.Vector2:
        return self.center.copy()


    @property
    def influence_radius(self) -> float:
        """
        Radius used by external systems
        (orbiting pieces, particles, future effects).

        This is intentionally larger than the visual radius.
        """
        return self.radius * 2.4


    def contains_point(self, point: tuple[float, float]) -> bool:
        """
        Returns True if a point lies within the event horizon.
        """
        dx = point[0] - self.center.x
        dy = point[1] - self.center.y
        return dx * dx + dy * dy <= self.radius ** 2