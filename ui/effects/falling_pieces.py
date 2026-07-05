from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame


@dataclass(slots=True)
class FallingObject:

    sprite: pygame.Surface

    x: float
    y: float

    speed: float

    drift_amplitude: float
    drift_speed: float
    drift_phase: float

    rotation: float
    rotation_speed: float

    scale: float

    velocity_scale: float = 1.0

    #
    # Polish-1
    #

    base_scale: float = 1.0


class FallingSystem:

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
    ):

        self.width = width
        self.height = height

        self.random = random.Random(seed)

        self.objects: list[FallingObject] = []

        self.time = 0.0

        self._transform_cache: dict[
            tuple[int, int, int],
            pygame.Surface,
        ] = {}

    # --------------------------------------------------

    def resize(
        self,
        width: int,
        height: int,
    ):

        self.width = width
        self.height = height

    def _get_transformed(
        self,
        obj: FallingObject,
    ) -> pygame.Surface:

        angle = int(obj.rotation) % 360

        scale_key = int(
            obj.scale
            * obj.base_scale
            * 100
        )

        key = (
            id(obj.sprite),
            angle,
            scale_key,
        )

        cached = self._transform_cache.get(key)

        if cached is not None:
            return cached

        transformed = pygame.transform.rotozoom(

            obj.sprite,

            obj.rotation,

            obj.scale
            * obj.base_scale,

        )

        self._transform_cache[key] = transformed

        if len(self._transform_cache) > 1500:
            self._transform_cache.clear()

        return transformed

    # --------------------------------------------------

    def add(
        self,
        sprite: pygame.Surface,
        *,
        base_scale: float = 1.0,
    ):

        self.objects.append(

            FallingObject(

                sprite=sprite,

                x=self.random.uniform(
                    0,
                    self.width,
                ),

                y=self.random.uniform(
                    -self.height,
                    self.height,
                ),

                speed=self.random.uniform(
                    35,
                    110,
                ),

                drift_amplitude=self.random.uniform(
                    15,
                    60,
                ),

                drift_speed=self.random.uniform(
                    0.2,
                    1.2,
                ),

                drift_phase=self.random.uniform(
                    0,
                    math.tau,
                ),

                rotation=self.random.uniform(
                    0,
                    360,
                ),

                rotation_speed=self.random.uniform(
                    -35,
                    35,
                ),

                scale=self.random.uniform(
                    0.70,
                    1.10,
                ),

                base_scale=base_scale,
            )
        )

    # --------------------------------------------------

    def clear(self):

        self.objects.clear()

    # --------------------------------------------------

    def update(
        self,
        dt: float,
    ):

        self.time += dt

        for obj in self.objects:

            obj.velocity_scale = min(
                obj.velocity_scale + dt * 0.08,
                1.0,
            )

            obj.y += (
                obj.speed
                * obj.velocity_scale
                * dt
            )

            obj.rotation += (
                obj.rotation_speed
                * dt
            )

            if obj.y > self.height + 200:

                obj.y = -200

                obj.x = self.random.uniform(
                    0,
                    self.width,
                )

    # --------------------------------------------------

    def draw(
        self,
        surface: pygame.Surface,
    ):

        draw_list = []

        for obj in self.objects:

            x = (
                obj.x
                + math.sin(
                    self.time
                    * obj.drift_speed
                    + obj.drift_phase
                )
                * obj.drift_amplitude
            )

            draw_list.append(
                (
                    obj.y,
                    x,
                    obj,
                )
            )

        draw_list.sort(
            key=lambda item: item[0]
        )

        for y, x, obj in draw_list:

            sprite = self._get_transformed(obj)

            rect = sprite.get_rect()

            rect.center = (
                round(x),
                round(y),
            )

            surface.blit(
                sprite,
                rect,
            )