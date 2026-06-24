from dataclasses import dataclass


@dataclass
class StatusEffect:
    name: str
    remaining_opponent_turns: int

    def tick(self):
        self.remaining_opponent_turns -= 1

    def expired(self):
        return self.remaining_opponent_turns <= 0


class FortunateStatus(StatusEffect):
    def __init__(self, duration=1):
        super().__init__(
            name="Fortunate",
            remaining_opponent_turns=duration
        )


class MisfortunateStatus(StatusEffect):
    def __init__(
        self,
        reduction_percent=0.30,
        duration=1,
        seed=0
    ):
        super().__init__(
            name="Misfortunate",
            remaining_opponent_turns=duration
        )

        self.reduction_percent = reduction_percent
        self.seed = seed