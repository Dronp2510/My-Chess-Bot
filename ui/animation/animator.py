"""
animator.py
===========

Global animation manager.

The Animator owns every active animation and timeline.

It updates them once per frame and automatically removes completed
animations.

The renderer is responsible for drawing.

The animator is responsible for movement.

Future Usage
------------
animator.add(Tween(...))

animator.add(Timeline(...))

animator.update(dt)
"""

from __future__ import annotations

from typing import List

from .animation import Animation
from .timeline import Timeline


class Animator:
    """
    Global animation manager.

    Supports running multiple animations and timelines in parallel.
    """

    def __init__(self) -> None:

        self._animations: List[Animation] = []

        self._timelines: List[Timeline] = []

        self.paused = False

    # ---------------------------------------------------------
    # Add
    # ---------------------------------------------------------

    def add(self, animation: Animation) -> Animation:
        """
        Register an animation.

        Returns the animation for optional chaining.
        """

        self._animations.append(animation)

        return animation

    def add_timeline(self, timeline: Timeline) -> Timeline:
        """
        Register a timeline.

        Returns the timeline for optional chaining.
        """

        self._timelines.append(timeline)

        return timeline

    # ---------------------------------------------------------
    # Remove
    # ---------------------------------------------------------

    def remove(self, animation: Animation) -> None:

        if animation in self._animations:
            self._animations.remove(animation)

    def remove_timeline(self, timeline: Timeline) -> None:

        if timeline in self._timelines:
            self._timelines.remove(timeline)

    # ---------------------------------------------------------
    # Control
    # ---------------------------------------------------------

    def pause(self) -> None:

        self.paused = True

        for animation in self._animations:
            animation.pause()

        for timeline in self._timelines:
            timeline.pause()

    def resume(self) -> None:

        self.paused = False

        for animation in self._animations:
            animation.resume()

        for timeline in self._timelines:
            timeline.resume()

    def clear(self) -> None:
        """
        Stop and remove every animation.
        """

        self._animations.clear()

        self._timelines.clear()

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Update every active animation.

        Completed animations are automatically removed.
        """

        if self.paused:
            return

        #
        # Individual animations
        #

        finished = []

        for animation in self._animations:

            animation.update(dt)

            if animation.is_finished:
                finished.append(animation)

        for animation in finished:
            self._animations.remove(animation)

        #
        # Timelines
        #

        finished = []

        for timeline in self._timelines:

            timeline.update(dt)

            if timeline.finished:
                finished.append(timeline)

        for timeline in finished:
            self._timelines.remove(timeline)

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    @property
    def animation_count(self) -> int:
        """
        Number of active animations.
        """

        return len(self._animations)

    @property
    def timeline_count(self) -> int:
        """
        Number of active timelines.
        """

        return len(self._timelines)

    @property
    def active_count(self) -> int:
        """
        Total active animation objects.
        """

        return (
            len(self._animations)
            + len(self._timelines)
        )

    @property
    def is_idle(self) -> bool:
        """
        True if nothing is currently animating.
        """

        return self.active_count == 0

    # ---------------------------------------------------------
    # Debug
    # ---------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"Animator("
            f"animations={len(self._animations)}, "
            f"timelines={len(self._timelines)})"
        )