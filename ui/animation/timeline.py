"""
timeline.py
===========

Timeline coordinates multiple animations.

Animations are executed sequentially.

Example
-------

timeline.add(fade_in)
timeline.wait(0.25)
timeline.add(slide_in)
timeline.wait(0.15)
timeline.add(glow)

Future Usage
------------
- Main menu intro
- Screen transitions
- Victory sequence
- Ability cinematics
- Campaign events
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Optional

from .animation import Animation


class Wait(Animation):
    """
    Simple delay animation.

    Used internally by Timeline.
    """

    def __init__(self, duration: float):

        super().__init__(duration=duration)

    def apply(self, progress: float) -> None:
        pass


class Timeline:
    """
    Executes animations one after another.
    """

    def __init__(self) -> None:

        self._queue: Deque[Animation] = deque()

        self._current: Optional[Animation] = None

        self.running = True

        self.paused = False

    # ---------------------------------------------------------
    # Queue
    # ---------------------------------------------------------

    def add(self, animation: Animation) -> "Timeline":
        """
        Queue an animation.

        Returns
        -------
        Timeline

        Enables fluent chaining:

            timeline.add(a).wait(0.2).add(b)
        """

        self._queue.append(animation)

        return self

    def wait(self, seconds: float) -> "Timeline":
        """
        Insert a delay.
        """

        self._queue.append(
            Wait(seconds)
        )

        return self

    def clear(self) -> None:
        """
        Remove every queued animation.
        """

        self._queue.clear()

        self._current = None

    # ---------------------------------------------------------
    # Control
    # ---------------------------------------------------------

    def pause(self) -> None:

        self.paused = True

        if self._current:
            self._current.pause()

    def resume(self) -> None:

        self.paused = False

        if self._current:
            self._current.resume()

    def stop(self) -> None:

        self.running = False

        self._queue.clear()

        self._current = None

    def restart(self) -> None:

        self.running = True

        self.paused = False

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(self, dt: float) -> None:

        if not self.running:
            return

        if self.paused:
            return

        #
        # Load next animation
        #

        if self._current is None:

            if not self._queue:
                return

            self._current = self._queue.popleft()

        #
        # Update current animation
        #

        self._current.update(dt)

        #
        # Move to next animation
        #

        if self._current.is_finished:

            self._current = None

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def finished(self) -> bool:
        """
        Returns True when the timeline
        has no more work to perform.
        """

        return (
            self._current is None
            and not self._queue
        )

    @property
    def animation_count(self) -> int:
        """
        Number of queued animations.
        """

        return len(self._queue)

    @property
    def current_animation(self) -> Optional[Animation]:
        """
        Currently executing animation.
        """

        return self._current

    # ---------------------------------------------------------
    # Debug
    # ---------------------------------------------------------

    def __len__(self) -> int:

        return len(self._queue)

    def __repr__(self) -> str:

        return (
            f"Timeline("
            f"queued={len(self._queue)}, "
            f"running={self.running}, "
            f"finished={self.finished})"
        )