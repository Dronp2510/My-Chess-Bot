
class GameState:

    def __init__(self):

        self.board = [
                        ["br","bkn","bb","bq","bk","bb","bkn","br"],
                        ["bp","bp","bp","bp","bp","bp","bp","bp"],
                        ["--","--","--","--","--","--","--","--"],
                        ["--","--","--","--","--","--","--","--"],
                        ["--","--","--","--","--","--","--","--"],
                        ["--","--","--","--","--","--","--","--"],
                        ["wp","wp","wp","wp","wp","wp","wp","wp"],
                        ["wr","wkn","wb","wq","wk","wb","wkn","wr"]
                    ]
        
        self.white_to_move = True
        self.move_log = []
        
        self.checkmate = False
        self.stalemate = False

        self.castling_rights = {
            'wks': True,
            'wqs': True,
            'bks': True,
            'bqs': True
        }

        self.en_passent_square = ()

    def make_move(self, move):

        sr = move.start_row
        sc = move.start_col

        er = move.end_row
        ec = move.end_col

        piece = move.piece_moved

        # move piece
        self.board[er][ec] = piece
        self.board[sr][sc] = "--"

        # pawn promotion
        if move.is_pawn_promotion:

            promoted_piece = piece[0] + "q"
            self.board[er][ec] = promoted_piece

        self.move_log.append(move)

        # =========================
        # UPDATE CASTLING RIGHTS
        # =========================

        if piece == "wk":
            self.castling_rights["wks"] = False
            self.castling_rights["wqs"] = False

        elif piece == "bk":
            self.castling_rights["bks"] = False
            self.castling_rights["bqs"] = False

        elif piece == "wr":

            if sr == 7 and sc == 0:
                self.castling_rights["wqs"] = False

            elif sr == 7 and sc == 7:
                self.castling_rights["wks"] = False

        elif piece == "br":

            if sr == 0 and sc == 0:
                self.castling_rights["bqs"] = False

            elif sr == 0 and sc == 7:
                self.castling_rights["bks"] = False

        # =========================
        # HANDLE CASTLING MOVE
        # =========================

        if move.is_castle_move:

            # king-side
            if ec == 6:

                self.board[er][5] = self.board[er][7]
                self.board[er][7] = "--"

            # queen-side
            elif ec == 2:

                self.board[er][3] = self.board[er][0]
                self.board[er][0] = "--"

        self.white_to_move = not self.white_to_move

    def undo_move(self):

        if len(self.move_log) == 0:
            return

        move = self.move_log.pop()

        sr = move.start_row
        sc = move.start_col

        er = move.end_row
        ec = move.end_col

        # restore moved piece
        self.board[sr][sc] = move.piece_moved

        # restore captured piece
        self.board[er][ec] = move.piece_captured

        # undo castling rook move
        if move.is_castle_move:

            # king-side
            if ec == 6:

                self.board[er][7] = self.board[er][5]
                self.board[er][5] = "--"

            # queen-side
            elif ec == 2:

                self.board[er][0] = self.board[er][3]
                self.board[er][3] = "--"

        # switch turns back
        self.white_to_move = not self.white_to_move