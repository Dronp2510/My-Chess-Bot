from game.path_base import PathBase
from game.paths.fortune_abilities import (
    LuckyOne,
    UnluckyOne,
    ArmyOfLuck,
    ArmyOfUnluck
)


FORTUNE_STAGE_DATA = {

    5: {
        "max_cz": 5,
        "recovery": 1,

        "lucky_targets": 1,
        "unlucky_targets": 1,

        "army_luck_percent": 0.30,
        "army_unluck_percent": 0.20,

        "move_reduction": 0.30,

        "fortunate_duration": 1,
        "misfortunate_duration": 1,
    },

    4: {
        "max_cz": 8,
        "recovery": 2,

        "lucky_targets": 1,
        "unlucky_targets": 1,

        "army_luck_percent": 0.30,
        "army_unluck_percent": 0.20,

        "move_reduction": 0.30,

        "fortunate_duration": 1,
        "misfortunate_duration": 1,
    },

    3: {
        "max_cz": 10,
        "recovery": 2,

        "lucky_targets": 3,
        "unlucky_targets": 2,

        "army_luck_percent": 0.30,
        "army_unluck_percent": 0.20,

        "move_reduction": 0.30,

        "fortunate_duration": 1,
        "misfortunate_duration": 1,
    },

    2: {
        "max_cz": 15,
        "recovery": 3,

        "lucky_targets": 3,
        "unlucky_targets": 2,

        "army_luck_percent": 0.30,
        "army_unluck_percent": 0.20,

        "move_reduction": 0.30,

        "fortunate_duration": 2,
        "misfortunate_duration": 1,
    },

    1: {
        "max_cz": 20,
        "recovery": 6,

        "lucky_targets": 3,
        "unlucky_targets": 2,

        "army_luck_percent": 0.30,
        "army_unluck_percent": 0.20,

        "move_reduction": 0.30,

        "fortunate_duration": 2,
        "misfortunate_duration": 1,
    },

    0: {
        "max_cz": 25,
        "recovery": 10,

        "lucky_targets": 5,
        "unlucky_targets": 3,

        "army_luck_percent": 0.60,
        "army_unluck_percent": 0.50,

        "move_reduction": 0.50,

        "fortunate_duration": 2,
        "misfortunate_duration": 2,
    }
}


class FortunePath(PathBase):

    def __init__(self, stage=5):
        super().__init__(stage)

    def get_abilities(self):

        abilities = [
            LuckyOne(),
            UnluckyOne()
        ]

        if self.stage <= 2:
            abilities.append(ArmyOfLuck())

        if self.stage <= 1:
            abilities.append(ArmyOfUnluck())

        return abilities

    def get_config(self):
        return FORTUNE_STAGE_DATA[self.stage]

    def get_max_cz(self):
        return self.get_config()["max_cz"]

    def get_recovery(self):
        return self.get_config()["recovery"]

    def get_lucky_targets(self):
        return self.get_config()["lucky_targets"]

    def get_unlucky_targets(self):
        return self.get_config()["unlucky_targets"]

    def get_army_luck_percent(self):
        return self.get_config()["army_luck_percent"]

    def get_army_unluck_percent(self):
        return self.get_config()["army_unluck_percent"]

    def get_move_reduction(self):
        return self.get_config()["move_reduction"]

    def get_fortunate_duration(self):
        return self.get_config()["fortunate_duration"]

    def get_misfortunate_duration(self):
        return self.get_config()["misfortunate_duration"]