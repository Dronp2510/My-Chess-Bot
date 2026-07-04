"""
renderer.py
============

Central rendering pipeline for War Chess.

Responsibilities
----------------
- Maintain render layers.
- Queue renderable objects.
- Draw everything in the correct order.
- Remain completely independent from game logic.

The renderer intentionally does NOT know anything about:
    • Chess
    • Widgets
    • Particles
    • Screens
    • Animations

Every drawable object simply implements:

    render(surface)

and is submitted to a render layer.

Future systems such as the Main Menu, Battle UI,
Particles, Tooltips and Effects all use this renderer.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from .layers import RenderLayer


class Renderer:
    """
    Central rendering manager.

    Objects are submitted into ordered render layers.

    Example
    -------
        renderer.begin_frame()

        renderer.submit(background, RenderLayer.BACKGROUND)
        renderer.submit(board, RenderLayer.WORLD)
        renderer.submit(button, RenderLayer.UI)

        renderer.render(screen)
    """

    def __init__(self) -> None:

        # Dictionary:
        #
        # {
        #     RenderLayer.BACKGROUND : [...],
        #     RenderLayer.WORLD      : [...],
        #     ...
        # }

        self._layers: Dict[RenderLayer, List] = defaultdict(list)

    # ---------------------------------------------------------
    # Frame Management
    # ---------------------------------------------------------

    def begin_frame(self) -> None:
        """
        Clears the render queues.

        Should be called exactly once at the beginning
        of every frame.
        """

        self._layers.clear()

    # ---------------------------------------------------------
    # Queue Submission
    # ---------------------------------------------------------

    def submit(self, renderable, layer: RenderLayer) -> None:
        """
        Submit an object to a render layer.

        The object must implement:

            render(surface)

        Parameters
        ----------
        renderable
            Drawable object.

        layer
            Target render layer.
        """

        self._layers[layer].append(renderable)

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------

    def render(self, surface) -> None:
        """
        Draw every queued object.

        Layers are rendered in ascending order.
        """

        for layer in RenderLayer:

            if layer not in self._layers:
                continue

            for renderable in self._layers[layer]:

                if not renderable.is_visible:
                    continue

                renderable.render(surface)

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def clear_layer(self, layer: RenderLayer) -> None:
        """
        Removes every object from one layer.
        """

        self._layers[layer].clear()

    def layer_count(self, layer: RenderLayer) -> int:
        """
        Returns the number of queued objects
        inside a render layer.
        """

        return len(self._layers[layer])

    def total_renderables(self) -> int:
        """
        Returns the total number of queued
        renderables for the current frame.
        """

        return sum(len(objects) for objects in self._layers.values())