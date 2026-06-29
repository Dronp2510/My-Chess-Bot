from abc import ABC, abstractmethod


class Ability(ABC):

    def __init__(self,name,cost,consumes_turn=False):
        
        self.name = name
        self.cost = cost
        self.consumes_turn = consumes_turn

    # ----------------------------------------
    # Target validation
    # ----------------------------------------

    def validate_target(self,gs,battle_state,square,owner_color,):
        """
        Default implementation.

        Abilities with targets should override this.
        """
        return False

    @abstractmethod
    def activate(self, battle_state, **kwargs):
        pass