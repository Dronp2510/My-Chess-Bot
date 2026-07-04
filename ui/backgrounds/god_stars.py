from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from ui.backgrounds.background import Background
from ui import config


OUTER_GLOW = (120, 60, 210)
MID_GLOW = (170, 90, 255)
CORE = (230, 180, 255)


@dataclass(slots=True)
class GodStar:
    x: float
    y: float

    radius: float

    glow_radius: float

    pulse_speed: float
    pulse_phase: float

    base_alpha: int


class GodStars(Background):
    """
    Large mystical stars representing the
    influence of the Outer Gods.
    """

    def __init__(
        self,
        width: int,
        height: int,
        count: int = config.GOD_STAR_COUNT,
        seed: int | None = None,
    ):
        super().__init__()

        self.width = width
        self.height = height

        self.count = count

        self.random = random.Random(seed)

        self.time = 0.0

        self.stars: list[GodStar] = []

        self._generate()

    # -----------------------------------------------------

    def _generate(self):

        self.stars.clear()

        attempts = 0

        while (
            len(self.stars) < self.count
            and attempts < self.count * 30
        ):
            attempts += 1

            radius = self.random.uniform(4.0, 7.5)

            x = self.random.uniform(radius, self.width - radius)
            y = self.random.uniform(radius, self.height - radius)

            valid = True

            for star in self.stars:

                dx = x - star.x
                dy = y - star.y

                minimum = (
                    radius
                    + star.radius
                    + 80
                )

                if dx * dx + dy * dy < minimum * minimum:
                    valid = False
                    break

            if not valid:
                continue

            self.stars.append(
                GodStar(
                    x=x,
                    y=y,
                    radius=radius,
                    glow_radius=radius * 5,
                    pulse_speed=self.random.uniform(0.15, 0.45),
                    pulse_phase=self.random.uniform(0, math.tau),
                    base_alpha=self.random.randint(120, 190),
                )
            )

    # -----------------------------------------------------

    def resize(self, width: int, height: int):

        self.width = width
        self.height = height

        self._generate()

    # -----------------------------------------------------

    def update(self, dt: float):

        self.time += dt

    # -----------------------------------------------------

    def draw(self, surface: pygame.Surface):

        if not self.enabled:
            return

        for star in self.stars:

            pulse = (
                math.sin(
                    self.time * star.pulse_speed
                    + star.pulse_phase
                )
                * 0.5
                + 0.5
            )

            glow_radius = star.glow_radius * (
                0.9 + pulse * 0.2
            )

            glow_surface = pygame.Surface(
                (
                    int(glow_radius * 2),
                    int(glow_radius * 2),
                ),
                pygame.SRCALPHA,
            )

            center = (
                int(glow_radius),
                int(glow_radius),
            )

            pygame.draw.circle(
                glow_surface,
                (*OUTER_GLOW, int(star.base_alpha * 0.18)),
                center,
                int(glow_radius),
            )

            pygame.draw.circle(
                glow_surface,
                (*MID_GLOW, int(star.base_alpha * 0.35)),
                center,
                int(glow_radius * 0.6),
            )

            pygame.draw.circle(
                glow_surface,
                (*CORE, star.base_alpha),
                center,
                int(star.radius),
            )

            surface.blit(
                glow_surface,
                (
                    star.x - glow_radius,
                    star.y - glow_radius,
                ),
            )

    def get_stars(self) -> tuple[GodStar, ...]:
        """
        Returns an immutable view of the generated God Stars.

        Other systems (e.g. black hole, future shaders, particle emitters)
        can query star positions without mutating the internal list.
        """
        return tuple(self.stars)