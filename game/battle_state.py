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

    def clear_statuses(self, square):
        """
        Drop any status effects sitting on a square, without moving them
        anywhere. Needed for en passant: the captured pawn's square is
        NOT the mover's end_square, so move_piece_status() alone leaves a
        ghost status entry behind (Issue D in the review). Call this with
        the *actual* captured square whenever a piece is removed from the
        board other than via a normal move-to-end_square capture.
        """
        if square in self.statuses:
            del self.statuses[square]

    def get_status(self, square, status_name):

        for status in self.get_statuses(square):

            if status.name == status_name:
                return status

        return None

    def snapshot_statuses(self):
        """
        Cheap snapshot for move undo. Returns {} (not None) when there are
        no statuses, so callers can always unconditionally restore without
        a None-check -- that ambiguity (None meaning "no snapshot taken"
        vs. "snapshot of an empty state") was part of Issue F.

        Uses a shallow copy.copy() per StatusEffect instead of
        copy.deepcopy() on the whole dict: StatusEffect subclasses only
        hold plain ints/strings, so a shallow copy is equivalent but far
        cheaper, and this runs on every make_move() inside the search tree.
        """
        if not self.statuses:
            return {}

        return {
            square: [copy.copy(effect) for effect in effects]
            for square, effects in self.statuses.items()
        }

    def restore_statuses(self, snapshot):
        self.statuses.clear()
        if snapshot:
            self.statuses.update(snapshot)