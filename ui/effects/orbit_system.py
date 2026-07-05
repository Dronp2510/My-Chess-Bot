from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from ui import config


@dataclass(slots=True)
class OrbitObject:
    """
    Generic orbiting renderable.

    Designed to support any future sprite:
        • Chess pieces
        • Artifacts
        • Boss icons
        • Relics
        • Ability icons

    Rendering data lives here so OrbitSystem
    remains completely asset-agnostic.
    """

    sprite: pygame.Surface

    angle: float

    radius: float

    orbit_speed: float

    rotation_speed: float

    self_rotation: float

    clockwise: bool

    orbit_x_scale: float

    orbit_y_scale: float

    #
    # New (Polish-1)
    #

    base_scale: float = 1.0

    min_scale: float = 0.65

    max_scale: float = 1.00


class OrbitSystem:

    def __init__(
        self,
        center,
        seed: int | None = None,
    ):

        self.center = pygame.Vector2(center)

        self.random = random.Random(seed)

        self.objects: list[OrbitObject] = []

    # --------------------------------------------------

    def set_center(self, center):

        self.center.update(center)

    # --------------------------------------------------

    def add(
        self,
        sprite: pygame.Surface,
        *,
        base_scale: float = 1.0,
    ):

        self.objects.append(

            OrbitObject(

                sprite=sprite,

                angle=self.random.uniform(
                    0,
                    math.tau,
                ),

                radius=self.random.uniform(
                    config.ORBIT_MIN_RADIUS,
                    config.ORBIT_MAX_RADIUS,
                ),

                orbit_speed=self.random.uniform(
                    config.ORBIT_MIN_SPEED,
                    config.ORBIT_MAX_SPEED,
                ),

                rotation_speed=self.random.uniform(
                    -16,
                    16,
                ),

                self_rotation=self.random.uniform(
                    0,
                    360,
                ),

                clockwise=self.random.choice(
                    (True, False)
                ),

                orbit_x_scale=self.random.uniform(
                    0.88,
                    1.12,
                ),

                orbit_y_scale=self.random.uniform(
                    0.82,
                    1.08,
                ),

                base_scale=base_scale,

            )
        )

    # --------------------------------------------------

    def clear(self):

        self.objects.clear()

    # --------------------------------------------------

    def update(self, dt):

        for obj in self.objects:

            direction = -1 if obj.clockwise else 1

            obj.angle += (
                direction
                * obj.orbit_speed
                * dt
            )

            obj.self_rotation += (
                obj.rotation_speed
                * dt
            )

    # --------------------------------------------------

    def draw(self, surface):

        draw_list = []

        for obj in self.objects:

            x = (
                self.center.x
                + math.cos(obj.angle)
                * obj.radius
                * obj.orbit_x_scale
            )

            y = (
                self.center.y
                + math.sin(obj.angle)
                * obj.radius
                * obj.orbit_y_scale
            )

            #
            # Fake perspective
            #

            depth = (
                math.sin(obj.angle)
                + 1
            ) * 0.5

            scale = (
                obj.min_scale
                + depth
                * (obj.max_scale - obj.min_scale)
            )

            scale *= obj.base_scale

            draw_list.append(
                (
                    y,
                    x,
                    scale,
                    obj,
                )
            )

        draw_list.sort(key=lambda item: item[0])

        for _, x, scale, obj in draw_list:

            rotated = pygame.transform.rotozoom(

                obj.sprite,

                obj.self_rotation,

                scale,

            )

            rect = rotated.get_rect(
                center=(x, _)
            )

            surface.blit(
                rotated,
                rect,
            )

    def remove(self, obj: OrbitObject):
        if obj in self.objects:
            self.objects.remove(obj)


    def __len__(self):
        return len(self.objects)