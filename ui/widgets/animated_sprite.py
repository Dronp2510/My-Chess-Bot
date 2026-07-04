"""
animated_sprite.py

Animated image widget.

Extends the Image widget with frame-based animation support while
remaining compatible with the UI animation system.

Features
--------
- Named animations
- Play / Pause / Stop
- Looping animations
- Animation speed multiplier
- Automatic frame advancement
- Animator integration
"""

from __future__ import annotations

from typing import Dict, List, Optional

import pygame

from .image import Image


class AnimatedSprite(Image):
    """
    Image widget capable of playing frame-based animations.

    Animations are supplied as:

        {
            "idle": [Surface, Surface, ...],
            "hover": [...],
            "glow": [...]
        }
    """

    def __init__(
        self,
        rect: pygame.Rect,
        animations: Optional[Dict[str, List[pygame.Surface]]] = None,
        fps: float = 12.0,
        visible: bool = True,
    ) -> None:
        super().__init__(rect, image=None, visible=visible)

        self.animations = animations or {}

        self.current_animation: Optional[str] = None

        self.current_frame = 0

        self.frame_timer = 0.0

        self.fps = max(1.0, fps)

        self.speed = 1.0

        self.loop = True

        self.playing = False

    # ------------------------------------------------------------------
    # Animation Management
    # ------------------------------------------------------------------

    def add_animation(
        self,
        name: str,
        frames: List[pygame.Surface],
    ) -> None:
        self.animations[name] = frames

    def has_animation(self, name: str) -> bool:
        return name in self.animations

    def play(
        self,
        name: str,
        *,
        loop: bool = True,
        restart: bool = False,
    ) -> None:
        """
        Starts playing an animation.
        """

        if name not in self.animations:
            return

        if (
            self.current_animation == name
            and self.playing
            and not restart
        ):
            return

        self.current_animation = name
        self.current_frame = 0
        self.frame_timer = 0.0

        self.loop = loop
        self.playing = True

        self.image = self.animations[name][0]

    def stop(self) -> None:
        self.playing = False
        self.current_frame = 0
        self.frame_timer = 0.0

    def pause(self) -> None:
        self.playing = False

    def resume(self) -> None:
        if self.current_animation is not None:
            self.playing = True

    def set_speed(self, multiplier: float) -> None:
        self.speed = max(0.01, multiplier)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Updates both property animations and sprite animations.
        """

        super().update(dt)

        if (
            not self.playing
            or self.current_animation is None
        ):
            return

        frames = self.animations.get(self.current_animation)

        if not frames:
            return

        frame_duration = 1.0 / (self.fps * self.speed)

        self.frame_timer += dt

        while self.frame_timer >= frame_duration:

            self.frame_timer -= frame_duration

            self.current_frame += 1

            if self.current_frame >= len(frames):

                if self.loop:
                    self.current_frame = 0

                else:
                    self.current_frame = len(frames) - 1
                    self.playing = False
                    break

            self.image = frames[self.current_frame]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @property
    def frame_count(self) -> int:
        if self.current_animation is None:
            return 0

        return len(
            self.animations.get(
                self.current_animation,
                [],
            )
        )

    @property
    def is_playing(self) -> bool:
        return self.playing

    def reset(self) -> None:
        self.current_frame = 0
        self.frame_timer = 0.0

        if (
            self.current_animation
            and self.frame_count > 0
        ):
            self.image = self.animations[
                self.current_animation
            ][0]