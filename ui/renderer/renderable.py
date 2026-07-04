"""
renderable.py
=============

Base class for every drawable object in the War Chess UI framework.

The renderer never knows what kind of object it is rendering.
It only expects every submitted object to implement:

    render(surface)

Future subclasses include:

    • Widget
    • Panel
    • Button
    • Label
    • Image
    • AnimatedSprite
    • ParticleEmitter
    • Background
    • Screen Effects
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .layers import RenderLayer


class Renderable(ABC):
    """
    Base renderable object.

    Every drawable object in the UI engine should inherit from this
    class and implement the render() method.
    """

    def __init__(self, layer: RenderLayer = RenderLayer.UI) -> None:
        """
        Parameters
        ----------
        layer
            Default render layer for this object.
        """

        self.layer = layer

        # Visibility flag.
        # Hidden objects remain alive but are skipped during rendering.
        self.visible = True

        # Reserved for future animation engine.
        self.opacity = 255

        # Reserved for future scene graph / widgets.
        self.enabled = True

    # ---------------------------------------------------------
    # State Management
    # ---------------------------------------------------------

    def show(self) -> None:
        """Make the object visible."""
        self.visible = True

    def hide(self) -> None:
        """Hide the object."""
        self.visible = False

    def enable(self) -> None:
        """Enable the object."""
        self.enabled = True

    def disable(self) -> None:
        """Disable the object."""
        self.enabled = False

    # ---------------------------------------------------------
    # Optional Update Hook
    # ---------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Optional per-frame update.

        Subclasses may override this if they need animation or
        internal state updates.

        Parameters
        ----------
        dt
            Delta time in seconds.
        """
        pass

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------

    @abstractmethod
    def render(self, surface) -> None:
        """
        Draw this object onto the supplied surface.

        Parameters
        ----------
        surface
            Target pygame surface.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement render()."
        )

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    @property
    def is_visible(self) -> bool:
        """Returns whether the object should be rendered."""
        return self.visible and self.enabled