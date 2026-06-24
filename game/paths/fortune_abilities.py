import math
import random

from game.ability_base import Ability
from game.status_effects import (
    FortunateStatus,
    MisfortunateStatus
)

class LuckyOne(Ability):

    def __init__(self):
        super().__init__(
            name="Lucky One",
            cost=2
        )

    def activate(
        self,
        battle_state,
        targets
    ):

        if not battle_state.cz.spend(self.cost):
            return False

        path = battle_state.path

        max_targets = path.get_lucky_targets()

        targets = targets[:max_targets]

        for square in targets:

            battle_state.add_status(
                square,
                FortunateStatus(
                    duration=path.get_fortunate_duration()
                )
            )

        return True

class UnluckyOne(Ability):

    def __init__(self):
        super().__init__(
            name="Unlucky One",
            cost=4
        )

    def activate(
        self,
        battle_state,
        targets
    ):

        if not battle_state.cz.spend(self.cost):
            return False

        path = battle_state.path

        max_targets = path.get_unlucky_targets()

        targets = targets[:max_targets]

        for square in targets:

            seed = random.randint(
                0,
                2**31 - 1
            )

            battle_state.add_status(
                square,
                MisfortunateStatus(
                    reduction_percent=
                        path.get_move_reduction(),
                    duration=
                        path.get_misfortunate_duration(),
                    seed=seed
                )
            )

        return True

class ArmyOfLuck(Ability):

    def __init__(self):
        super().__init__(
            name="Army Of Luck",
            cost=10,
            consumes_turn=True
        )

    def activate(
        self,
        battle_state,
        friendly_squares
    ):

        if not battle_state.cz.spend(self.cost):
            return False

        path = battle_state.path

        count = max(
            1,
            math.floor(
                len(friendly_squares)
                * path.get_army_luck_percent()
            )
        )

        chosen = random.sample(
            friendly_squares,
            min(count, len(friendly_squares))
        )

        for square in chosen:

            battle_state.add_status(
                square,
                FortunateStatus(
                    duration=
                        path.get_fortunate_duration()
                )
            )

        return True

class ArmyOfUnluck(Ability):

    def __init__(self):
        super().__init__(
            name="Army Of Unluck",
            cost=15,
            consumes_turn=True
        )

    def activate(
        self,
        battle_state,
        enemy_squares
    ):

        if not battle_state.cz.spend(self.cost):
            return False

        path = battle_state.path

        count = max(
            1,
            math.floor(
                len(enemy_squares)
                * path.get_army_unluck_percent()
            )
        )

        chosen = random.sample(
            enemy_squares,
            min(count, len(enemy_squares))
        )

        for square in chosen:

            seed = random.randint(
                0,
                2**31 - 1
            )

            battle_state.add_status(
                square,
                MisfortunateStatus(
                    reduction_percent=
                        path.get_move_reduction(),
                    duration=
                        path.get_misfortunate_duration(),
                    seed=seed
                )
            )

        return True

