from game.path_base import PathBase


FORTUNE_STAGE_DATA = {

    5: {
        "max_cz": 5,
        "recovery": 1
    },

    4: {
        "max_cz": 8,
        "recovery": 2
    },

    3: {
        "max_cz": 10,
        "recovery": 2
    },

    2: {
        "max_cz": 15,
        "recovery": 3
    },

    1: {
        "max_cz": 20,
        "recovery": 6
    },

    0: {
        "max_cz": 25,
        "recovery": 10
    }
}


class FortunePath(PathBase):

    def __init__(self, stage=5):
        super().__init__(stage)

    def get_max_cz(self):
        return FORTUNE_STAGE_DATA[self.stage]["max_cz"]

    def get_recovery(self):
        return FORTUNE_STAGE_DATA[self.stage]["recovery"]

    def get_abilities(self):
        return []