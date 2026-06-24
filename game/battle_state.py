import copy
from collections import defaultdict

from game.conceptualization import CZPool


class BattleState:

    def __init__(self, path):

        self.path = path

        self.cz = CZPool(
            max_cz=path.get_max_cz(),
            recovery=path.get_recovery()
        )

        self.statuses = defaultdict(list)

    def add_status(self, piece_key, status):
        self.statuses[piece_key].append(status)

    def get_statuses(self, piece_key):
        return self.statuses.get(piece_key, [])

    def has_status(self, piece_key, status_name):

        for status in self.get_statuses(piece_key):
            if status.name == status_name:
                return True

        return False

    def tick_statuses_for_color(self, color):

        expired_squares = []

        for square, effects in self.statuses.items():

            for effect in effects:

                if effect.owner_color == color:
                    effect.tick()

            effects[:] = [
                effect
                for effect in effects
                if not effect.expired()
            ]

            if not effects:
                expired_squares.append(square)

        for square in expired_squares:
            del self.statuses[square]
                 
    def move_piece_status(self, start_square, end_square):

        if start_square not in self.statuses:
            return

        self.statuses[end_square] = self.statuses.pop(start_square)

    def get_status(self, square, status_name):

        for status in self.get_statuses(square):

            if status.name == status_name:
                return status

        return None
    
    def snapshot_statuses(self):
        return copy.deepcopy(self.statuses)
    
    def restore_statuses(self, snapshot):
        self.statuses.clear()
        self.statuses.update(snapshot)