

class Move:

    ranks_to_rows = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0
    }

    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7
    }

    cols_to_files = {v: k for k, v in files_to_cols.items()}

    # For Redable Moves
    files_to_cols = {
        'a':0, 'b':1, 'c':2, 'd':3,
        'e':4, 'f':5, 'g':6, 'h':7
    }

    cols_to_files = {v:k for k,v in files_to_cols.items()}

    ranks_to_rows = {
        '1':7, '2':6, '3':5, '4':4,
        '5':3, '6':2, '7':1, '8':0
    }

    rows_to_ranks = {v:k for k,v in ranks_to_rows.items()}

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]
    
    def get_chess_notation(self):

        if self.is_castle_move:
            if self.end_col == 6:
                return "O-O"
            return "O-O-O"

        move_string = (
            self.get_rank_file(self.start_row, self.start_col) +
            self.get_rank_file(self.end_row, self.end_col)
        )

        if self.is_pawn_promotion:
            move_string += "Q"

        return move_string
    
    def __str__(self):
        return self.get_chess_notation()
        
    # End


    def __init__(self, start_sq, end_sq, board):

        self.start_row = start_sq[0]
        self.start_col = start_sq[1]

        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # pawn promotion
        self.is_pawn_promotion = False

        if (
            self.piece_moved == "wp" and self.end_row == 0
        ) or (
            self.piece_moved == "bp" and self.end_row == 7
        ):
            self.is_pawn_promotion = True

        # castling
        self.is_castle_move = False

        # en passant
        self.is_en_passant_move = False

        # castle
        if self.piece_moved[1:] == "k":
            if abs(self.start_col - self.end_col) == 2:
                self.is_castle_move = True

        # en passant capture
        if self.piece_moved[1:] == "p":

            if self.start_col != self.end_col and self.piece_captured == "--":

                self.is_en_passant_move = True

                if self.piece_moved[0] == "w":
                    self.piece_captured = "bp"

                else:
                    self.piece_captured = "wp"
        
        # unique move id
        self.move_id = (
            self.start_row * 1000 +
            self.start_col * 100 +
            self.end_row * 10 +
            self.end_col
        )

        # previous game state info
        self.prev_en_passant_square = ()
        self.prev_castling_rights = {}

        self.prev_hash = 0
        
    def __eq__(self, other):

        if isinstance(other, Move):
            return self.move_id == other.move_id

        return False

    def get_chess_notation(self):

        return (
            self.get_rank_file(self.start_row, self.start_col)
            +
            self.get_rank_file(self.end_row, self.end_col)
        )

    def get_rank_file(self, row, col):

        return (
            self.cols_to_files[col]
            +
            self.rows_to_ranks[row]
        )