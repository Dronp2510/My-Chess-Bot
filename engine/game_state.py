from engine.move import Move
from engine.fen import board_to_fen, fen_to_board, metadata_to_string, string_to_metadata
from engine.zobrist import compute_full_hash
from engine.constants import (ROOK_DIRECTIONS, QUEEN_DIRECTIONS, BISHOP_DIRECTIONS, 
                                KNIGHT_OFFSETS, KING_OFFSETS, ROOK, BISHOP, QUEEN)

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

        self.null_move_stack = []
        
        self.make_move_calls = 0
        self.undo_move_calls = 0
        self.attack_calls = 0
        self.valid_move_calls = 0
        self.all_valid_move_calls = 0

        # Zobrist Hashing
        self.position_hash = 0
        self.initialize_hash()

        # FEN Notation
        self.metadata = {
            "powers": {},
            "status_effects": {},
            "campaign": {},
        }
        self.halfmove_clock = 0
        self.fullmove_number = 1

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def is_on_board(row, col):
        return 0 <= row < 8 and 0 <= col < 8

    @staticmethod
    def enemy_color(color):
        return "b" if color == "w" else "w"

    def current_color(self):
        return "w" if self.white_to_move else "b"

    def current_king_position(self, color):

        if color == "w":
            return self.white_king_pos

        return self.black_king_pos
    

    def _castling_string(self):

        rights = ""

        if self.castling_rights["wks"]:
            rights += "K"

        if self.castling_rights["wqs"]:
            rights += "Q"

        if self.castling_rights["bks"]:
            rights += "k"

        if self.castling_rights["bqs"]:
            rights += "q"

        return rights if rights else "-"

    def _enpassant_string(self):
        if not self.en_passant_square:
            return "-"

        row, col = self.en_passant_square

        file_char = chr(ord("a") + col)
        rank_char = str(8 - row)

        return file_char + rank_char

    def to_fen(self):
        board_part = board_to_fen(self.board)

        stm = "w" if self.white_to_move else "b"

        castling = self._castling_string()

        ep = self._enpassant_string()

        return (
            f"{board_part} "
            f"{stm} "
            f"{castling} "
            f"{ep} "
            f"{self.halfmove_clock} "
            f"{self.fullmove_number}"
        )

    def to_extended_fen(self):

        base = self.to_fen()

        metadata = metadata_to_string(self.metadata)

        return base + " " + metadata

    def from_fen(self, fen):

        parts = fen.strip().split()

        if len(parts) < 6:
            raise ValueError("Invalid FEN")

        board_part = parts[0]
        stm = parts[1]
        castling = parts[2]
        ep = parts[3]
        halfmove = int(parts[4])
        fullmove = int(parts[5])

        self.board = fen_to_board(board_part)

        self.white_to_move = stm == "w"

        self.halfmove_clock = halfmove
        self.fullmove_number = fullmove

        self.en_passant_square = ()

        if ep != "-":
            col = ord(ep[0]) - ord("a")
            row = 8 - int(ep[1])

            self.en_passant_square = (row, col)

        self.castling_rights["wks"] = "K" in castling
        self.castling_rights["wqs"] = "Q" in castling
        self.castling_rights["bks"] = "k" in castling
        self.castling_rights["bqs"] = "q" in castling

        self.move_log.clear()

        self.metadata = {}

        self._refresh_after_fen()

    def from_extended_fen(self, fen):

        parts = fen.strip().split(maxsplit=6)

        if len(parts) < 6:
            raise ValueError("Invalid Extended FEN")

        normal_fen = " ".join(parts[:6])

        self.from_fen(normal_fen)

        if len(parts) == 7:
            self.metadata = string_to_metadata(parts[6])

    def _refresh_after_fen(self):

        self.white_king_pos = None
        self.black_king_pos = None

        for r in range(8):
            for c in range(8):

                piece = self.board[r][c]

                if piece == "wk":
                    self.white_king_pos = (r, c)

                elif piece == "bk":
                    self.black_king_pos = (r, c)

        self.position_hash = compute_full_hash(self)

    def _update_castling_rights(self, move):

        sr = move.start_row
        sc = move.start_col

        er = move.end_row
        ec = move.end_col

        piece = move.piece_moved

        # =========================
        # MOVED PIECE
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
        # CAPTURED ROOK
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

    def _handle_castle_rook_move(self,move,zobrist_piece_keys):

        if not move.is_castle_move:
            return

        er = move.end_row
        ec = move.end_col

        # king side
        if ec == 6:

            rook = self.board[er][7]

            self.position_hash ^= (
                zobrist_piece_keys[rook][er][7]
            )

            self.board[er][5] = rook
            self.board[er][7] = "--"

            self.position_hash ^= (
                zobrist_piece_keys[rook][er][5]
            )

        # queen side
        elif ec == 2:

            rook = self.board[er][0]

            self.position_hash ^= (
                zobrist_piece_keys[rook][er][0]
            )

            self.board[er][3] = rook
            self.board[er][0] = "--"

            self.position_hash ^= (
                zobrist_piece_keys[rook][er][3]
            )

    def _update_en_passant_square( self, piece, sr, sc, er):

        if piece[1:] == "p" and abs(sr - er) == 2:

            self.en_passant_square = (
                (sr + er) // 2,
                sc
            )

        else:

            self.en_passant_square = ()

    def _update_king_position(self, piece, row, col):

        if piece == "wk":
            self.white_king_pos = (row, col)

        elif piece == "bk":
            self.black_king_pos = (row, col)

    def make_move(self, move):
        # counting calls 
        self.make_move_calls += 1
        
        from engine.zobrist import (
            zobrist_piece_keys,
            side_to_move_key,
            castling_keys,
            en_passant_keys
        )

        sr = move.start_row
        sc = move.start_col

        er = move.end_row
        ec = move.end_col

        move.prev_hash = self.position_hash
        piece = move.piece_moved
        self.position_hash ^= zobrist_piece_keys[piece][sr][sc]

        # saving previous king pos.
        move.prev_white_king_pos = self.white_king_pos
        move.prev_black_king_pos = self.black_king_pos

        # remove old en passant hash
        if self.en_passant_square:
            self.position_hash ^= \
                en_passant_keys[self.en_passant_square[1]]

        # remove old castling rights hash
        for right, enabled in self.castling_rights.items():
            if enabled:
                self.position_hash ^= castling_keys[right]

        if move.piece_captured != '--' and not move.is_en_passant_move:

            self.position_hash ^= \
                zobrist_piece_keys[
                    move.piece_captured
                ][er][ec]

        # move piece
        self.board[er][ec] = piece

        moved_piece = move.piece_moved
        captured_piece = move.piece_captured

        if moved_piece[1:] == "p" or captured_piece != "--":
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if not self.white_to_move:
            self.fullmove_number += 1
        
        # save previous state for undo
        move.prev_en_passant_square = self.en_passant_square

        move.prev_castling_rights = self.castling_rights.copy()


        if move.is_en_passant_move:
            captured_row = sr

            self.position_hash ^= \
                zobrist_piece_keys[
                    move.piece_captured
                ][captured_row][ec]
            self.board[sr][ec] = '--'

        self.board[sr][sc] = "--"

        # Pawn promotion
        if move.is_pawn_promotion:

            promoted_piece = piece[0] + "q"

            self.board[er][ec] = promoted_piece

            self.position_hash ^= \
                zobrist_piece_keys[
                    promoted_piece
                ][er][ec]

        else:

            self.position_hash ^= \
                zobrist_piece_keys[piece][er][ec]

        self.move_log.append(move)

        # =========================
        # UPDATE CASTLING RIGHTS
        # =========================
        
        self._update_castling_rights(move)

        # =========================
        # HANDLE CASTLING MOVE
        # =========================

        self._handle_castle_rook_move(move, zobrist_piece_keys)

        # update en passant square
        self._update_en_passant_square(piece, sr, sc, er)

        if self.en_passant_square:

            self.position_hash ^= \
                en_passant_keys[
                    self.en_passant_square[1]
                ]
            
        self._update_king_position(piece, er, ec)
            
        for right, enabled in self.castling_rights.items():

            if enabled:
                self.position_hash ^= castling_keys[right]
        
        self.position_hash ^= side_to_move_key
        self.white_to_move = not self.white_to_move

    def undo_move(self):    

        # counting calls
        self.undo_move_calls += 1

        if len(self.move_log) == 0:
            return

        move = self.move_log.pop()
        self.position_hash = move.prev_hash

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

    def make_null_move(self):
        from engine.zobrist import side_to_move_key, en_passant_keys

        # Save only what null-move changes.
        self.null_move_stack.append((
            self.position_hash,
            self.en_passant_square,
            self.white_to_move
        ))

        # Remove old en-passant hash if present.
        if self.en_passant_square:
            self.position_hash ^= en_passant_keys[self.en_passant_square[1]]

        # Null move clears en passant.
        self.en_passant_square = ()

        # Toggle side to move.
        self.position_hash ^= side_to_move_key
        self.white_to_move = not self.white_to_move


    def undo_null_move(self):
        if not self.null_move_stack:
            return

        self.position_hash, self.en_passant_square, self.white_to_move = self.null_move_stack.pop()
    
    def get_pseudo_moves(self, position):

        row, col = position

        piece = self.board[row][col]

        if piece == "--":
            return []

        piece_type = piece[1:]
        color = piece[0]

        moves = self.move_functions[piece_type](
            row,
            col,
            color
        )

        # add castling pseudo moves
        if piece_type == 'k':
            moves += self.get_castling_moves(
                row,
                col,
                color
            )

        pseudo_moves = []

        for end_square in moves:

            pseudo_moves.append(
                Move(position, end_square, self.board)
            )

        return pseudo_moves
    
    def get_all_pseudo_moves(self):

        all_moves = []

        current_color = self.current_color()

        for row in range(8):
            for col in range(8):

                piece = self.board[row][col]

                if piece != "--" and piece[0] == current_color:

                    moves = self.get_pseudo_moves((row, col))

                    if moves:
                        all_moves.extend(moves)

        return all_moves
    
    def get_valid_moves(self, position):

        legal_moves = []

        piece = self.board[position[0]][position[1]]

        if piece == "--":
            return legal_moves

        color = piece[0]

        enemy_color = self.enemy_color(color)

        pseudo_moves = self.get_pseudo_moves(position)

        for move in pseudo_moves:

            self.make_move(move)

            king_pos = self.current_king_position(color)

            if not self.is_square_attacked(king_pos[0], king_pos[1], enemy_color):
                legal_moves.append(move)

            self.undo_move()

        return legal_moves

    def get_all_valid_moves(self):

        # counting calls
        self.all_valid_move_calls += 1

        all_moves = []

        current_color = self.current_color()

        for row in range(8):
            for col in range(8):

                piece = self.board[row][col]

                if piece != "--" and piece[0] == current_color:

                    moves = self.get_valid_moves((row, col))

                    if moves:
                        all_moves.extend(moves)

        return all_moves

    def is_in_check(self):

        current_color = self.current_color()

        king_pos = self.current_king_position(
            current_color
        )

        enemy_color = self.enemy_color(
            current_color
        )

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

    def _sliding_attack_exists( self, row, col, enemy_color, directions, attacking_pieces):

        for dr, dc in directions:

            for distance in range(1, 8):

                r = row + dr * distance
                c = col + dc * distance

                if not self.is_on_board(r, c):
                    break

                piece = self.board[r][c]

                if piece == "--":
                    continue

                if (
                    piece[0] == enemy_color
                    and piece[1:] in attacking_pieces
                ):
                    return True

                break

        return False

    def is_square_attacked(self, row, col, enemy_color):
        # counting calls
        self.attack_calls += 1

        board = self.board

        # =========================
        # PAWN ATTACKS
        # =========================

        if enemy_color == 'w':

            pawn_rows = row + 1

            if pawn_rows < 8:

                if col - 1 >= 0 and board[pawn_rows][col - 1] == "wp":
                    return True

                if col + 1 < 8 and board[pawn_rows][col + 1] == "wp":
                    return True

        else:

            pawn_rows = row - 1

            if pawn_rows >= 0:

                if col - 1 >= 0 and board[pawn_rows][col - 1] == "bp":
                    return True

                if col + 1 < 8 and board[pawn_rows][col + 1] == "bp":
                    return True

        # =========================
        # KNIGHT ATTACKS
        # =========================

        enemy_knight = enemy_color + "kn"

        for dr, dc in KNIGHT_OFFSETS:

            r = row + dr
            c = col + dc

            if self.is_on_board(r, c):

                if board[r][c] == enemy_knight:
                    return True

        # =========================
        # KING ATTACKS
        # =========================

        enemy_king = enemy_color + "k"

        for dr, dc in KING_OFFSETS:

            r = row + dr
            c = col + dc

            if self.is_on_board(r, c):

                if board[r][c] == enemy_king:
                    return True

        # =========================
        # ROOK / QUEEN ATTACKS
        # =========================

        if self._sliding_attack_exists(
            row,
            col,
            enemy_color,
            ROOK_DIRECTIONS,
            {ROOK, QUEEN}
        ):
            return True

        # =========================
        # BISHOP / QUEEN ATTACKS
        # =========================

        if self._sliding_attack_exists(
            row,
            col,
            enemy_color,
            BISHOP_DIRECTIONS,
            {BISHOP, QUEEN}
        ):
            return True

        return False

    def _castle_path_is_safe(self, row, enemy_color, empty_squares, safe_squares):

        for col in empty_squares:

            if self.board[row][col] != "--":
                return False

        for col in safe_squares:

            if self.is_square_attacked(
                row,
                col,
                enemy_color
            ):
                return False

        return True
    
    def get_castling_moves(self, row, col, color):

        moves = []

        enemy_color = self.enemy_color(color)

        if self.board[row][col] != f"{color}k":
            return moves

        # king cannot castle while in check
        if self.is_square_attacked( row, col, enemy_color):
            return moves

        home_row = 7 if color == "w" else 0

        kingside_right = (
            "wks"
            if color == "w"
            else "bks"
        )

        queenside_right = (
            "wqs"
            if color == "w"
            else "bqs"
        )

        # =========================
        # KING SIDE
        # =========================

        if self.castling_rights[kingside_right]:

            if self._castle_path_is_safe( home_row, enemy_color, empty_squares=(5, 6), safe_squares=(5, 6)):
                moves.append((home_row, 6))

        # =========================
        # QUEEN SIDE
        # =========================

        if self.castling_rights[queenside_right]:

            if self._castle_path_is_safe( home_row, enemy_color, empty_squares=(1, 2, 3), safe_squares=(2, 3)):
                moves.append((home_row, 2))

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

        return self.loop_moves(
            row,
            col,
            color,
            ROOK_DIRECTIONS
        )

    def get_bishop_moves(self, row, col, color):

        return self.loop_moves(
            row,
            col,
            color,
            BISHOP_DIRECTIONS
        )

    def get_queen_moves(self, row, col, color):

        return self.loop_moves(
            row,
            col,
            color,
            QUEEN_DIRECTIONS
        )

    def get_king_moves(self, row, col, color):

        moves = []

        for dr, dc in KING_OFFSETS:

            new_row = row + dr
            new_col = col + dc

            if self.is_on_board(new_row, new_col):

                target = self.board[new_row][new_col]

                if target == "--" or target[0] != color:
                    moves.append((new_row, new_col))

        return moves

    def get_knight_moves(self, row, col, color):

        moves = []

        for dr, dc in KNIGHT_OFFSETS:

            new_row = row + dr
            new_col = col + dc

            if self.is_on_board(new_row, new_col):

                target = self.board[new_row][new_col]

                if target == "--" or target[0] != color:
                    moves.append((new_row, new_col))

        return moves

    def get_pawn_moves(self, row, col, color):

        moves = []

        direction = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1

        one_step_row = row + direction

        # ============================================================
        # FORWARD MOVES
        # ============================================================

        if ( self.is_on_board(one_step_row, col) and self.board[one_step_row][col] == "--"):

            moves.append((one_step_row, col))

            two_step_row = row + (2 * direction)

            if ( row == start_row and self.board[two_step_row][col] == "--"):
                moves.append((two_step_row, col))

        # ============================================================
        # CAPTURES
        # ============================================================

        for capture_col in (col - 1, col + 1):

            if not self.is_on_board( one_step_row, capture_col):
                continue

            target = self.board[one_step_row][capture_col]

            # normal capture
            if ( target != "--" and target[0] != color):
                moves.append((
                        one_step_row,
                        capture_col
                    ))

            # en passant
            elif (self.en_passant_square and (one_step_row, capture_col) == self.en_passant_square):
                moves.append((
                        one_step_row,
                        capture_col
                    ))

        return moves
    
    def move_is_legal(self):

        # side that JUST moved
        moving_color = (
            "b"
            if self.white_to_move
            else "w"
        )

        king_pos = self.current_king_position(
            moving_color
        )

        enemy_color = self.enemy_color(
            moving_color
        )

        return not self.is_square_attacked(
            king_pos[0],
            king_pos[1],
            enemy_color
        )

    def _current_side_piece(self, piece):

        if piece == "--":
            return False

        return (
            (piece[0] == "w" and self.white_to_move)
            or
            (piece[0] == "b" and not self.white_to_move)
        )
    
    def get_all_capture_moves(self):

        moves = []

        capture_generators = {
            "p": self.get_pawn_capture_moves,
            "r": self.get_rook_capture_moves,
            "kn": self.get_knight_capture_moves,
            "b": self.get_bishop_capture_moves,
            "q": self.get_queen_capture_moves,
            "k": self.get_king_capture_moves,
        }

        for row in range(8):
            for col in range(8):

                piece = self.board[row][col]

                if not self._current_side_piece(piece):
                    continue

                capture_generators[
                    piece[1:]
                ](
                    row,
                    col,
                    moves
                )

        return moves
    
    def get_pawn_capture_moves(self, row, col, moves):

        piece_color = self.board[row][col][0]

        if piece_color == 'w':
            directions = [(-1, -1), (-1, 1)]
            promotion_row = 0
        else:
            directions = [(1, -1), (1, 1)]
            promotion_row = 7

        for dr, dc in directions:

            end_row = row + dr
            end_col = col + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:

                end_piece = self.board[end_row][end_col]

                # Normal capture
                if end_piece != '--' and end_piece[0] != piece_color:

                    is_promotion = end_row == promotion_row

                    moves.append(
                        Move(
                            (row, col),
                            (end_row, end_col),
                            self.board
                            # is_pawn_promotion=is_promotion
                        )
                    )

                # En passant
                elif (end_row, end_col) == self.en_passant_square:

                    moves.append(
                        Move(
                            (row, col),
                            (end_row, end_col),
                            self.board
                            # is_en_passant_move=True
                        )
                    )

    def get_knight_capture_moves(self, row, col, moves):

        ally_color = self.board[row][col][0]

        for dr, dc in KNIGHT_OFFSETS:

            end_row = row + dr
            end_col = col + dc

            if not self.is_on_board(end_row, end_col):
                continue

            end_piece = self.board[end_row][end_col]

            if ( end_piece != "--" and end_piece[0] != ally_color ):
                moves.append(Move((row, col), (end_row, end_col), self.board))

    def _sliding_capture_moves(self, row, col, directions, moves):

        ally_color = self.board[row][col][0]

        for dr, dc in directions:

            for distance in range(1, 8):

                end_row = row + dr * distance
                end_col = col + dc * distance

                if not self.is_on_board(end_row,end_col):
                    break

                end_piece = self.board[end_row][end_col]

                if end_piece == "--":
                    continue

                if end_piece[0] != ally_color:

                    moves.append(Move((row, col),(end_row, end_col),self.board))

                break

    def get_rook_capture_moves(self, row, col, moves):

        self._sliding_capture_moves(row, col, ROOK_DIRECTIONS, moves)

    def get_bishop_capture_moves(self, row, col, moves):

        self._sliding_capture_moves(row, col, BISHOP_DIRECTIONS, moves)

    def get_king_capture_moves(self, row, col, moves):

        ally_color = self.board[row][col][0]

        for dr, dc in KING_OFFSETS:

            end_row = row + dr
            end_col = col + dc

            if not self.is_on_board(end_row,end_col):
                continue

            end_piece = self.board[end_row][end_col]

            if (end_piece != "--" and end_piece[0] != ally_color):
                moves.append(Move((row, col),(end_row, end_col),self.board))

    def get_queen_capture_moves(self, row, col, moves):

        self.get_rook_capture_moves(row, col, moves)
        self.get_bishop_capture_moves(row, col, moves)

    def initialize_hash(self):

        from engine.zobrist import (
            zobrist_piece_keys,
            side_to_move_key,
            castling_keys,
            en_passant_keys
        )

        h = 0

        for row in range(8):
            for col in range(8):

                piece = self.board[row][col]

                if piece != "--":
                    h ^= zobrist_piece_keys[piece][row][col]

        if self.white_to_move:
            h ^= side_to_move_key

        for right, enabled in self.castling_rights.items():

            if enabled:
                h ^= castling_keys[right]

        if self.en_passant_square:

            ep_file = self.en_passant_square[1]
            h ^= en_passant_keys[ep_file]

        self.position_hash = h

    def verify_hash(self):

        current = self.position_hash

        self.initialize_hash()
        rebuilt = self.position_hash

        self.position_hash = current

        return current == rebuilt


if __name__ == "__main__":

    gs = GameState()

    fen = gs.to_fen()

    print("FEN:")
    print(fen)

    print()

    gs2 = GameState()

    gs2.from_fen(fen)

    print("Reconstructed:")
    print(gs2.to_fen())

    print()

    print("Match:", fen == gs2.to_fen())

    print("Hash OK:", gs.verify_hash())
    print("Hash OK After Load:", gs2.verify_hash())