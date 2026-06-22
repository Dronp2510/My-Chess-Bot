class Move:
    """
    Represents a chess move.

    Stores:
    - Start square
    - End square
    - Moved piece
    - Captured piece
    - Promotion information
    - Castling information
    - En passant information

    Also stores previous game-state data required for undo.
    """

    # ============================================================
    # BOARD COORDINATE CONVERSION
    # ============================================================

    FILES_TO_COLS = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7,
    }

    COLS_TO_FILES = {
        v: k for k, v in FILES_TO_COLS.items()
    }

    RANKS_TO_ROWS = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0,
    }

    ROWS_TO_RANKS = {
        v: k for k, v in RANKS_TO_ROWS.items()
    }

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self, start_sq, end_sq, board):

        self.start_row = start_sq[0]
        self.start_col = start_sq[1]

        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[
            self.start_row
        ][
            self.start_col
        ]

        self.piece_captured = board[
            self.end_row
        ][
            self.end_col
        ]

        # ========================================================
        # SPECIAL MOVE FLAGS
        # ========================================================

        self.is_pawn_promotion = self._is_pawn_promotion()

        self.is_castle_move = self._is_castle_move()

        self.is_en_passant_move = False

        self._detect_en_passant()

        # ========================================================
        # UNIQUE ID
        # ========================================================

        self.move_id = (
            self.start_row * 1000
            + self.start_col * 100
            + self.end_row * 10
            + self.end_col
        )

        # ========================================================
        # UNDO STATE
        # ========================================================

        self.prev_en_passant_square = ()
        self.prev_castling_rights = {}

        self.prev_hash = 0

        self.prev_white_king_pos = None
        self.prev_black_king_pos = None

    # ============================================================
    # SPECIAL MOVE DETECTION
    # ============================================================

    def _is_pawn_promotion(self):

        return (
            self.piece_moved == "wp"
            and self.end_row == 0
        ) or (
            self.piece_moved == "bp"
            and self.end_row == 7
        )

    def _is_castle_move(self):

        return (
            self.piece_moved[1:] == "k"
            and abs(self.start_col - self.end_col) == 2
        )

    def _detect_en_passant(self):

        if self.piece_moved[1:] != "p":
            return

        if (
            self.start_col != self.end_col
            and self.piece_captured == "--"
        ):

            self.is_en_passant_move = True

            if self.piece_moved[0] == "w":
                self.piece_captured = "bp"
            else:
                self.piece_captured = "wp"

    # ============================================================
    # NOTATION
    # ============================================================

    @classmethod
    def get_rank_file(cls, row, col):

        return (
            cls.COLS_TO_FILES[col]
            + cls.ROWS_TO_RANKS[row]
        )

    def get_chess_notation(self):

        if self.is_castle_move:

            if self.end_col == 6:
                return "O-O"

            return "O-O-O"

        move_string = (
            self.get_rank_file(
                self.start_row,
                self.start_col
            )
            +
            self.get_rank_file(
                self.end_row,
                self.end_col
            )
        )

        if self.is_pawn_promotion:
            move_string += "Q"

        return move_string

    # ============================================================
    # DUNDER METHODS
    # ============================================================

    def __str__(self):

        return self.get_chess_notation()

    def __repr__(self):

        return self.get_chess_notation()

    def __eq__(self, other):

        if isinstance(other, Move):
            return self.move_id == other.move_id

        return False

    def __hash__(self):

        return hash(self.move_id)