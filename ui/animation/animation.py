"""
animation.py
============

Base animation class used throughout the War Chess UI framework.

The Animation class manages the lifecycle of an animation:

    Idle
      ↓
    Running
      ↓
    Finished

It provides:

    • Duration
    • Delay
    • Easing
    • Progress tracking
    • Completion callbacks
    • Pause / Resume
    • Delta-time updates

Subclasses only need to implement:

    apply(progress)

where progress is already eased and normalized.

Future subclasses include:

    • Tween
    • MoveAnimation
    • FadeAnimation
    • ScaleAnimation
    • RotationAnimation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional

from .easing import linear


class Animation(ABC):
    """
    Base animation class.

    Every animation derives from this class.
    """

    def __init__(
        self,
        duration: float,
        easing: Callable[[float], float] = linear,
        delay: float = 0.0,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:

        if duration <= 0:
            raise ValueError("Animation duration must be greater than zero.")

        self.duration = duration
        self.delay = max(0.0, delay)
        self.easing = easing

        self.on_complete = on_complete

        self.elapsed = 0.0

        self.running = True
        self.finished = False
        self.paused = False

    # ---------------------------------------------------------
    # Control
    # ---------------------------------------------------------

    def pause(self) -> None:
        """Pause the animation."""
        self.paused = True

    def resume(self) -> None:
        """Resume the animation."""
        self.paused = False

    def stop(self) -> None:
        """Immediately stop the animation."""
        self.running = False
        self.finished = True

    def restart(self) -> None:
        """Restart the animation from the beginning."""

        self.elapsed = 0.0
        self.running = True
        self.finished = False
        self.paused = False

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Advance the animation.

        Parameters
        ----------
        dt
            Delta time in seconds.
        """

        if self.finished:
            return

        if not self.running:
            return

        if self.paused:
            return

        self.elapsed += dt

        if self.elapsed < self.delay:
            return

        animation_time = self.elapsed - self.delay

        progress = min(animation_time / self.duration, 1.0)

        eased_progress = self.easing(progress)

        self.apply(eased_progress)

        if progress >= 1.0:
            self.finish()

    # ---------------------------------------------------------
    # Finish
    # ---------------------------------------------------------

    def finish(self) -> None:
        """
        Marks the animation as complete.
        """

        if self.finished:
            return

        self.finished = True
        self.running = False

        # Ensure the animation ends
        # exactly at its final state.
        self.apply(1.0)

        if self.on_complete:
            self.on_complete()

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    @property
    def progress(self) -> float:
        """
        Current normalized progress.

        Returns
        -------
        float
            Value between 0 and 1.
        """

        if self.elapsed <= self.delay:
            return 0.0

        return min(
            (self.elapsed - self.delay) / self.duration,
            1.0,
        )

    @property
    def is_running(self) -> bool:
        """Whether the animation is currently active."""
        return self.running and not self.finished

    @property
    def is_finished(self) -> bool:
        """Whether the animation has completed."""
        return self.finished

    # ---------------------------------------------------------
    # Subclass Hook
    # ---------------------------------------------------------

    @abstractmethod
    def apply(self, progress: float) -> None:
        """
        Apply the animation.

        Parameters
        ----------
        progress
            Eased progress in the range [0, 1].
        """
        raise NotImplementedError