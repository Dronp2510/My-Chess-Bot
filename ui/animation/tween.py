"""
tween.py
========

Generic property interpolation animation.

Tween animates a single numeric property on an object.

Instead of creating dozens of animation classes, Tween can animate
nearly every UI property.

Examples
--------

Move widget:

    Tween(button, "x", 0, 300, 0.4)

Fade widget:

    Tween(panel, "opacity", 255, 0, 0.5)

Scale card:

    Tween(card, "scale", 1.0, 1.15, 0.2)

Rotate sprite:

    Tween(piece, "rotation", 0, 360, 1.5)

The target object only needs to expose the property.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from .animation import Animation
from .easing import linear


class Tween(Animation):
    """
    Generic property interpolation.

    Parameters
    ----------
    target
        Object whose property will be animated.

    property_name
        Name of the attribute.

    start_value
        Initial value.

    end_value
        Final value.

    duration
        Animation duration in seconds.
    """

    def __init__(
        self,
        target: Any,
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: Callable[[float], float] = linear,
        delay: float = 0.0,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:

        super().__init__(
            duration=duration,
            easing=easing,
            delay=delay,
            on_complete=on_complete,
        )

        self.target = target
        self.property_name = property_name

        self.start_value = start_value
        self.end_value = end_value

        # Difference cached once for performance.
        self.delta = end_value - start_value

        # Initialize property immediately.
        setattr(
            self.target,
            self.property_name,
            self.start_value,
        )

    # ---------------------------------------------------------
    # Animation
    # ---------------------------------------------------------

    def apply(self, progress: float) -> None:
        """
        Apply interpolated value to the target object.
        """

        value = self.start_value + self.delta * progress

        setattr(
            self.target,
            self.property_name,
            value,
        )

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    @property
    def current_value(self) -> float:
        """
        Current interpolated property value.
        """

        return getattr(
            self.target,
            self.property_name,
        )

    def reverse(self) -> None:
        """
        Reverse the tween.

        Useful for hover animations,
        button expansion, etc.
        """

        self.start_value, self.end_value = (
            self.end_value,
            self.start_value,
        )

        self.delta = (
            self.end_value
            - self.start_value
        )

        self.restart()

    def clone(self) -> "Tween":
        """
        Create an identical tween.

        Useful when the same animation
        is reused multiple times.
        """

        return Tween(
            target=self.target,
            property_name=self.property_name,
            start_value=self.start_value,
            end_value=self.end_value,
            duration=self.duration,
            easing=self.easing,
            delay=self.delay,
            on_complete=self.on_complete,
        )

    def __repr__(self) -> str:
        return (
            f"Tween("
            f"{self.target!r}, "
            f"{self.property_name!r}, "
            f"{self.start_value}, "
            f"{self.end_value}, "
            f"duration={self.duration})"
        )