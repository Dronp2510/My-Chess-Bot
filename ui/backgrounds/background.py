from __future__ import annotations

from abc import ABC, abstractmethod


class Background(ABC):
    """
    Base class for procedural background systems.

    Examples
    --------
    - StarField
    - Dust
    - Fog
    - GodStars
    """

    def __init__(self):
        self.enabled = True

    def reset(self) -> None:
        """Reset internal state."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update animation."""

    @abstractmethod
    def draw(self, surface) -> None:
        """Draw to the screen."""