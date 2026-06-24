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

    def tick_statuses(self):

        expired = []

        for piece, effects in self.statuses.items():

            for effect in effects:
                effect.tick()

            effects[:] = [
                effect
                for effect in effects
                if not effect.expired()
            ]

            if not effects:
                expired.append(piece)

        for piece in expired:
            del self.statuses[piece]
    
    def move_piece_status(self, start_square, end_square):

        if start_square not in self.statuses:
            return

        self.statuses[end_square] = self.statuses.pop(start_square)

    def get_status(self, square, status_name):

        for status in self.get_statuses(square):

            if status.name == status_name:
                return status

        return None