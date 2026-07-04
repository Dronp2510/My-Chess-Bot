from __future__ import annotations

from abc import abstractmethod

from ui.backgrounds.background import Background


class AtmosphericLayer(Background):
    """
    Base class for slow-moving atmospheric effects.

    Examples
    --------
    - Dust
    - Fog
    - Smoke
    - Corruption mist
    """

    def __init__(self, width: int, height: int):
        super().__init__()

        self.width = width
        self.height = height

    def resize(self, width: int, height: int):

        self.width = width
        self.height = height

        self.reset()

    @abstractmethod
    def reset(self):
        ...

    @abstractmethod
    def update(self, dt: float):
        ...

    @abstractmethod
    def draw(self, surface):
        ...