from __future__ import annotations

import random

import pygame

from ui.backgrounds.atmosphere import AtmosphericLayer
from ui import config


class Fog(AtmosphericLayer):
    """
    Slow drifting fog layers.

    Implemented using large translucent circles
    for excellent performance.
    """

    def __init__(
        self,
        width: int,
        height: int,
        layers: int = config.FOG_LAYER_COUNT,
        seed: int | None = None,
    ):
        super().__init__(width, height)

        self.random = random.Random(seed)

        self.layer_count = layers

        self.layers = []

        self.reset()

    def reset(self):

        self.layers.clear()

        for _ in range(self.layer_count):

            size = self.random.randint(280, 520)

            self.layers.append({

                "x": self.random.uniform(-100, self.width),

                "y": self.random.uniform(-100, self.height),

                "radius": size,

                "alpha": self.random.randint(10, 22),

                "vx": self.random.uniform(-6, 6),

                "vy": self.random.uniform(-3, 3),

            })

    def update(self, dt):

        for layer in self.layers:

            layer["x"] += layer["vx"] * dt
            layer["y"] += layer["vy"] * dt

            r = layer["radius"]

            if layer["x"] < -r:
                layer["x"] = self.width + r

            elif layer["x"] > self.width + r:
                layer["x"] = -r

            if layer["y"] < -r:
                layer["y"] = self.height + r

            elif layer["y"] > self.height + r:
                layer["y"] = -r

    def draw(self, surface):

        if not self.enabled:
            return

        for layer in self.layers:

            r = int(layer["radius"])

            fog = pygame.Surface(
                (r * 2, r * 2),
                pygame.SRCALPHA,
            )

            pygame.draw.circle(

                fog,

                (70, 65, 95, layer["alpha"]),

                (r, r),

                r,

            )

            surface.blit(
                fog,
                (
                    layer["x"] - r,
                    layer["y"] - r,
                ),
            )