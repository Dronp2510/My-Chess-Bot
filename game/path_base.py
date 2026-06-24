from abc import ABC, abstractmethod


class PathBase(ABC):

    def __init__(self, stage):
        self.stage = stage

    @abstractmethod
    def get_max_cz(self):
        pass

    @abstractmethod
    def get_recovery(self):
        pass

    @abstractmethod
    def get_abilities(self):
        pass