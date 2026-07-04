from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from ui.backgrounds.background import Background
from ui import config


# ---------------------------------------------------------
# Star colors
# ---------------------------------------------------------

STAR_COLORS = (
    (255, 255, 255),
    (235, 240, 255),
    (255, 248, 225),
    (235, 225, 255),
)


# ---------------------------------------------------------
# Star
# ---------------------------------------------------------

@dataclass(slots=True)
class Star:
    x: float
    y: float

    radius: float

    base_alpha: float

    twinkle_speed: float
    twinkle_phase: float

    depth: float

    color: tuple[int, int, int]


# ---------------------------------------------------------
# Star Field
# ---------------------------------------------------------

class StarField(Background):
    """
    High-performance procedural star field.

    Features
    --------
    • Multi-depth stars
    • Smooth twinkling
    • Resolution independent
    • Window resize support
    • Parallax-ready
    """

    def __init__(
        self,
        width: int,
        height: int,
        star_count: int = config.STAR_COUNT,
        seed: int | None = None,
    ):
        super().__init__()

        self.width = width
        self.height = height

        self.star_count = star_count

        self.time = 0.0

        self.random = random.Random(seed)

        self.stars: list[Star] = []

        self._generate()

    # -----------------------------------------------------

    def _generate(self):

        self.stars.clear()

        for _ in range(self.star_count):

            depth = self.random.uniform(0.25, 1.0)

            radius = self.random.uniform(0.6, 2.4) * depth

            star = Star(
                x=self.random.uniform(0, self.width),
                y=self.random.uniform(0, self.height),

                radius=radius,

                base_alpha=self.random.uniform(130, 255),

                twinkle_speed=self.random.uniform(0.5, 2.5),

                twinkle_phase=self.random.uniform(0, math.tau),

                depth=depth,

                color=self.random.choice(STAR_COLORS),
            )

            self.stars.append(star)

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

            if (
                star.x < -star.radius
                or star.x > self.width + star.radius
                or star.y < -star.radius
                or star.y > self.height + star.radius
            ):
                continue

            twinkle = (
                math.sin(
                    self.time * star.twinkle_speed
                    + star.twinkle_phase
                )
                * 0.5
                + 0.5
            )

            alpha = int(
                star.base_alpha
                * (0.55 + 0.45 * twinkle)
            )

            alpha = max(0, min(255, alpha))

            color = (
                star.color[0],
                star.color[1],
                star.color[2],
                alpha,
            )

            pygame.draw.circle(
                surface,
                color,
                (int(star.x), int(star.y)),
                max(1, int(star.radius)),
            )