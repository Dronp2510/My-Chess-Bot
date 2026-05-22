from valid_moves import *
from engine.move import Move

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
        
        self.white_king_pos = (7,4)
        self.black_king_pos = (0,4)

        self.move_functions = {
            'p': self.get_pawn_moves,
            'r': self.get_rook_moves,
            'kn': self.get_knight_moves,
            'b': self.get_bishop_moves,
            'q': self.get_queen_moves,
            'k': self.get_king_moves
        }
        
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

        self.en_passant_square = ()

    def make_move(self, move):

        sr = move.start_row
        sc = move.start_col

        er = move.end_row
        ec = move.end_col

        piece = move.piece_moved

        # saving previous king pos.
        move.prev_white_king_pos = self.white_king_pos
        move.prev_black_king_pos = self.black_king_pos

        # move piece
        self.board[er][ec] = piece

        # save previous state for undo
        move.prev_en_passant_square = self.en_passant_square

        move.prev_castling_rights = self.castling_rights.copy()


        if move.is_en_passant_move:
            self.board[sr][ec] = "--"

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
        # ROOK CAPTURED
        # =========================

        captured = move.piece_captured

        if captured == "wr":

            if er == 7 and ec == 0:
                self.castling_rights["wqs"] = False

            elif er == 7 and ec == 7:
                self.castling_rights["wks"] = False

        elif captured == "br":

            if er == 0 and ec == 0:
                self.castling_rights["bqs"] = False

            elif er == 0 and ec == 7:
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

        # update en passant square
        if piece[1:] == "p" and abs(sr - er) == 2:

            self.en_passant_square = (
                (sr + er) // 2,
                sc
            )

        else:
            self.en_passant_square = ()
        
        if piece == 'wk':
            self.white_king_pos = (er , ec)
        elif piece == 'bk':
            self.black_king_pos = (er , ec)

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

        # undo en passant
        if move.is_en_passant_move:

            self.board[er][ec] = "--"

            self.board[sr][ec] = move.piece_captured

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
            
        # restore en passant state
        self.en_passant_square = move.prev_en_passant_square

        # restore castling rights
        self.castling_rights = move.prev_castling_rights

        # restore king positions
        self.white_king_pos = move.prev_white_king_pos
        self.black_king_pos = move.prev_black_king_pos

        # switch turns back
        self.white_to_move = not self.white_to_move

    def get_valid_moves(self, position):

        row, col = position
        piece = self.board[row][col]

        if piece == "--":
            return []

        piece_type = piece[1:]
        color = piece[0]

        moves = self.move_functions[piece_type]( row, col, color )

        if piece_type == 'k':
            moves += self.get_castling_moves( row, col, color )

        legal_moves = []

        enemy_color = 'b' if color == 'w' else 'w'

        for end_square in moves:

            move = Move(position, end_square, self.board)
            self.make_move(move)

            if color == 'w':
                king_pos = self.white_king_pos
            else:
                king_pos = self.black_king_pos

            if not self.is_square_attacked( king_pos[0], king_pos[1], enemy_color ):
                legal_moves.append(move)

            self.undo_move()

        return legal_moves

    def get_all_valid_moves(self):

        all_moves = []

        current_color = 'w' if self.white_to_move else 'b'

        for row in range(8):
            for col in range(8):

                piece = self.board[row][col]

                if piece != "--" and piece[0] == current_color:

                    moves = self.get_valid_moves((row, col))

                    if moves:
                        all_moves.extend(moves)

        return all_moves

    def is_in_check(self):

        current_color = 'w' if self.white_to_move else 'b'

        if current_color == 'w':
            king_pos = self.white_king_pos
        else:
            king_pos = self.black_king_pos

        enemy_color = 'b' if current_color == 'w' else 'w'

        return self.is_square_attacked(
            king_pos[0],
            king_pos[1],
            enemy_color
        )

    def get_game_state(self):

        all_moves = self.get_all_valid_moves()

        if len(all_moves) == 0:

            if self.is_in_check():

                self.checkmate = True
                return "checkmate"

            else:

                self.stalemate = True
                return "stalemate"

        self.checkmate = False
        self.stalemate = False

        return "ongoing"
    
    def find_king(self, color):

        for row in range(8):
            for col in range(8):

                if self.board[row][col] == f"{color}k":
                    return (row, col)

        return None

    def is_square_attacked(self, row, col, enemy_color):

        for r in range(8):
            for c in range(8):

                piece = self.board[r][c]

                if piece != "--" and piece[0] == enemy_color:

                    piece_type = piece[1:]

                    # pawns handled separately
                    if piece_type == 'p':

                        direction = -1 if enemy_color == 'w' else 1

                        attack_squares = []

                        if 0 <= r + direction < 8:

                            if 0 <= c - 1 < 8:
                                attack_squares.append((r + direction, c - 1))

                            if 0 <= c + 1 < 8:
                                attack_squares.append((r + direction, c + 1))

                        moves = attack_squares

                    else:

                        moves = self.move_functions[piece_type]( r, c, enemy_color )

                    if (row, col) in moves:
                        return True

        return False

    def get_castling_moves(self, row, col, color):

        moves = []

        enemy = 'b' if color == 'w' else 'w'

        if self.board[row][col] != f"{color}k":
            return moves

        # king cannot castle while in check
        if self.is_square_attacked(row, col, enemy):
            return moves

        # WHITE
        if color == "w":

            # king-side
            if self.castling_rights["wks"]:

                if self.board[7][5] == "--" and \
                   self.board[7][6] == "--":

                    if not self.is_square_attacked(7, 5, enemy) and \
                       not self.is_square_attacked(7, 6, enemy):

                        moves.append((7, 6))

            # queen-side
            if self.castling_rights["wqs"]:

                if self.board[7][1] == "--" and \
                   self.board[7][2] == "--" and \
                   self.board[7][3] == "--":

                    if not self.is_square_attacked(7, 2, enemy) and \
                       not self.is_square_attacked(7, 3, enemy):

                        moves.append((7, 2))

        # BLACK
        else:

            # king-side
            if self.castling_rights["bks"]:

                if self.board[0][5] == "--" and \
                   self.board[0][6] == "--":

                    if not self.is_square_attacked(0, 5, enemy) and \
                       not self.is_square_attacked(0, 6, enemy):

                        moves.append((0, 6))

            # queen-side
            if self.castling_rights["bqs"]:

                if self.board[0][1] == "--" and \
                   self.board[0][2] == "--" and \
                   self.board[0][3] == "--":

                    if not self.is_square_attacked(0, 2, enemy) and \
                       not self.is_square_attacked(0, 3, enemy):

                        moves.append((0, 2))

        return moves

    def loop_moves(self, row, col, color, directions):

        moves = []

        for dr, dc in directions:

            for i in range(1, 8):

                new_row = row + dr * i
                new_col = col + dc * i

                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break

                target = self.board[new_row][new_col]

                if target == "--":

                    moves.append((new_row, new_col))

                else:

                    if target[0] != color:
                        moves.append((new_row, new_col))

                    break

        return moves

    def get_rook_moves(self, row, col, color):

        directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0)
        ]

        return self.loop_moves(
            row,
            col,
            color,
            directions
        )

    def get_bishop_moves(self, row, col, color):

        directions = [
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1)
        ]

        return self.loop_moves(
            row,
            col,
            color,
            directions
        )

    def get_queen_moves(self, row, col, color):

        directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1)
        ]

        return self.loop_moves(
            row,
            col,
            color,
            directions
        )

    def get_knight_moves(self, row, col, color):

        moves = []

        knight_moves = [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2)
        ]

        for dr, dc in knight_moves:

            new_row = row + dr
            new_col = col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:

                target = self.board[new_row][new_col]

                if target == "--" or target[0] != color:
                    moves.append((new_row, new_col))

        return moves

    def get_king_moves(self, row, col, color):

        moves = []

        king_moves = [
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0)
        ]

        for dr, dc in king_moves:

            new_row = row + dr
            new_col = col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:

                target = self.board[new_row][new_col]

                if target == "--" or target[0] != color:
                    moves.append((new_row, new_col))

        return moves

    def get_pawn_moves(self, row, col, color):

        moves = []

        direction = -1 if color == 'w' else 1

        start_row = 6 if color == 'w' else 1

        # single move
        if 0 <= row + direction < 8 and \
           self.board[row + direction][col] == "--":

            moves.append((row + direction, col))

            # double move
            if row == start_row and \
               self.board[row + 2 * direction][col] == "--":

                moves.append((row + 2 * direction, col))

        # capture left
        if 0 <= col - 1 < 8 and \
           0 <= row + direction < 8:

            target = self.board[row + direction][col - 1]

            if target != "--" and target[0] != color:

                moves.append((row + direction, col - 1))

        # capture right
        if 0 <= col + 1 < 8 and \
           0 <= row + direction < 8:

            target = self.board[row + direction][col + 1]

            if target != "--" and target[0] != color:

                moves.append((row + direction, col + 1))

        # en passant
        if self.en_passant_square:

            ep_row, ep_col = self.en_passant_square

            if row + direction == ep_row:

                if abs(col - ep_col) == 1:

                    moves.append((ep_row, ep_col))

        return moves