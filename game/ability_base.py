from abc import ABC, abstractmethod


class Ability(ABC):

    def __init__(
        self,
        name,
        cost,
        consumes_turn=False
    ):
        self.name = name
        self.cost = cost
        self.consumes_turn = consumes_turn

    @abstractmethod
    def activate(self, battle_state, **kwargs):
        pass