from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from ui.backgrounds.atmosphere import AtmosphericLayer
from ui import config


@dataclass(slots=True)
class DustParticle:
    x: float
    y: float

    radius: float

    alpha: int

    vx: float
    vy: float


class Dust(AtmosphericLayer):
    """
    Small drifting dust particles.

    Gives depth to otherwise static space.
    """

    def __init__(
        self,
        width: int,
        height: int,
        count: int = config.DUST_PARTICLE_COUNT,
        seed: int | None = None,
    ):
        super().__init__(width, height)

        self.random = random.Random(seed)

        self.count = count

        self.particles: list[DustParticle] = []

        self.reset()

    def reset(self):

        self.particles.clear()

        for _ in range(self.count):

            self.particles.append(

                DustParticle(

                    x=self.random.uniform(0, self.width),

                    y=self.random.uniform(0, self.height),

                    radius=self.random.uniform(1.0, 2.5),

                    alpha=self.random.randint(20, 70),

                    vx=self.random.uniform(-4, 4),

                    vy=self.random.uniform(-2, 2),

                )
            )

    def update(self, dt):

        for p in self.particles:

            p.x += p.vx * dt
            p.y += p.vy * dt

            if p.x < -10:
                p.x = self.width + 10

            elif p.x > self.width + 10:
                p.x = -10

            if p.y < -10:
                p.y = self.height + 10

            elif p.y > self.height + 10:
                p.y = -10

    def draw(self, surface):

        if not self.enabled:
            return

        for p in self.particles:

            pygame.draw.circle(
                surface,
                (220, 220, 220, p.alpha),
                (int(p.x), int(p.y)),
                max(1, int(p.radius)),
            )