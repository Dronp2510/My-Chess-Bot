from dataclasses import dataclass


@dataclass
class StatusEffect:
    name: str
    owner_color: str
    remaining_opponent_turns: int

    def tick(self):
        self.remaining_opponent_turns -= 1

    def expired(self):
        return self.remaining_opponent_turns <= 0


class FortunateStatus(StatusEffect):
    def __init__(self,owner_color,duration=1):
        super().__init__(
            name="Fortunate",
            owner_color=owner_color,
            remaining_opponent_turns=duration
        )


class MisfortunateStatus(StatusEffect):
    def __init__(
        self,
        owner_color,
        reduction_percent=0.30,
        duration=1,
        seed=0
    ):
        super().__init__(
            name="Misfortunate",
            owner_color=owner_color,
            remaining_opponent_turns=duration
        )

        self.reduction_percent = reduction_percent
        self.seed = seed