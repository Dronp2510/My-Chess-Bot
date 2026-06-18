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

        self.null_move_stack = []
        
        self.make_move_calls = 0
        self.undo_move_calls = 0
        self.attack_calls = 0
        self.valid_move_calls = 0
        self.all_valid_move_calls = 0

        # Zobrist Hashing
        self.position_hash = 0
        self.initialize_hash()

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
                rook = self.board[er][7]

                self.position_hash ^= \
                    zobrist_piece_keys[rook][er][7]

                self.board[er][5] = rook
                self.board[er][7] = "--"

                self.position_hash ^= \
                    zobrist_piece_keys[rook][er][5]

            # queen-side
            elif ec == 2:
                rook = self.board[er][0]

                self.position_hash ^= \
                    zobrist_piece_keys[rook][er][0]

                self.board[er][3] = rook
                self.board[er][0] = "--"

                self.position_hash ^= \
                    zobrist_piece_keys[rook][er][3]

        # update en passant square
        if piece[1:] == "p" and abs(sr - er) == 2:

            self.en_passant_square = (
                (sr + er) // 2,
                sc
            )

        else:
            self.en_passant_square = ()

        if self.en_passant_square:

            self.position_hash ^= \
                en_passant_keys[
                    self.en_passant_square[1]
                ]
            
        if piece == 'wk':
            self.white_king_pos = (er , ec)
        elif piece == 'bk':
            self.black_king_pos = (er , ec)
            
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

        current_color = 'w' if self.white_to_move else 'b'

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

        enemy_color = 'b' if color == 'w' else 'w'

        pseudo_moves = self.get_pseudo_moves(position)

        for move in pseudo_moves:

            self.make_move(move)

            if color == 'w':
                king_pos = self.white_king_pos
            else:
                king_pos = self.black_king_pos

            if not self.is_square_attacked(
                king_pos[0],
                king_pos[1],
                enemy_color
            ):
                legal_moves.append(move)

            self.undo_move()

        return legal_moves

    def get_all_valid_moves(self):
        # counting calls
        self.all_valid_move_calls += 1

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

        knight_offsets = [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2)
        ]

        enemy_knight = enemy_color + "kn"

        for dr, dc in knight_offsets:

            r = row + dr
            c = col + dc

            if 0 <= r < 8 and 0 <= c < 8:

                if board[r][c] == enemy_knight:
                    return True

        # =========================
        # KING ATTACKS
        # =========================

        king_offsets = [
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0)
        ]

        enemy_king = enemy_color + "k"

        for dr, dc in king_offsets:

            r = row + dr
            c = col + dc

            if 0 <= r < 8 and 0 <= c < 8:

                if board[r][c] == enemy_king:
                    return True

        # =========================
        # ROOK / QUEEN ATTACKS
        # =========================

        rook_directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0)
        ]

        for dr, dc in rook_directions:

            for i in range(1, 8):

                r = row + dr * i
                c = col + dc * i

                if not (0 <= r < 8 and 0 <= c < 8):
                    break

                piece = board[r][c]

                if piece == "--":
                    continue

                if piece[0] == enemy_color:

                    if piece[1:] == "r" or piece[1:] == "q":
                        return True

                break

        # =========================
        # BISHOP / QUEEN ATTACKS
        # =========================

        bishop_directions = [
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1)
        ]

        for dr, dc in bishop_directions:

            for i in range(1, 8):

                r = row + dr * i
                c = col + dc * i

                if not (0 <= r < 8 and 0 <= c < 8):
                    break

                piece = board[r][c]

                if piece == "--":
                    continue

                if piece[0] == enemy_color:

                    if piece[1:] == "b" or piece[1:] == "q":
                        return True

                break

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
    
    def move_is_legal(self):

        # side that JUST moved
        moving_color = 'b' if self.white_to_move else 'w'

        if moving_color == 'w':
            king_pos = self.white_king_pos
            enemy_color = 'b'
        else:
            king_pos = self.black_king_pos
            enemy_color = 'w'

        return not self.is_square_attacked(
            king_pos[0],
            king_pos[1],
            enemy_color
        )

    def get_all_capture_moves(self):

        moves = []

        for row in range(8):
            for col in range(8):

                piece = self.board[row][col]

                if piece == '--':
                    continue

                color = piece[0]

                if (color == 'w' and self.white_to_move) or \
                (color == 'b' and not self.white_to_move):

                    piece_type = piece[1:]

                    if piece_type == 'p':
                        self.get_pawn_capture_moves(row, col, moves)

                    elif piece_type == 'r':
                        self.get_rook_capture_moves(row, col, moves)

                    elif piece_type == 'kn':
                        self.get_knight_capture_moves(row, col, moves)

                    elif piece_type == 'b':
                        self.get_bishop_capture_moves(row, col, moves)

                    elif piece_type == 'q':
                        self.get_queen_capture_moves(row, col, moves)

                    elif piece_type == 'k':
                        self.get_king_capture_moves(row, col, moves)

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

        knight_moves = [
            (-2,-1), (-2,1),
            (-1,-2), (-1,2),
            (1,-2), (1,2),
            (2,-1), (2,1)
        ]

        ally_color = self.board[row][col][0]

        for dr, dc in knight_moves:

            end_row = row + dr
            end_col = col + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:

                end_piece = self.board[end_row][end_col]

                if end_piece != '--' and end_piece[0] != ally_color:

                    moves.append(
                        Move(
                            (row, col),
                            (end_row, end_col),
                            self.board
                        )
                    )

    def get_rook_capture_moves(self, row, col, moves):

        directions = [
            (-1,0),
            (1,0),
            (0,-1),
            (0,1)
        ]

        ally_color = self.board[row][col][0]

        for dr, dc in directions:

            for i in range(1, 8):

                end_row = row + dr * i
                end_col = col + dc * i

                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break

                end_piece = self.board[end_row][end_col]

                if end_piece == '--':
                    continue

                if end_piece[0] != ally_color:

                    moves.append(
                        Move(
                            (row, col),
                            (end_row, end_col),
                            self.board
                        )
                    )

                break

    def get_bishop_capture_moves(self, row, col, moves):

        directions = [
            (-1,-1),
            (1,1),
            (1,-1),
            (-1,1)
        ]

        ally_color = self.board[row][col][0]

        for dr, dc in directions:

            for i in range(1, 8):

                end_row = row + dr * i
                end_col = col + dc * i

                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break

                end_piece = self.board[end_row][end_col]

                if end_piece == '--':
                    continue

                if end_piece[0] != ally_color:

                    moves.append(
                        Move(
                            (row, col),
                            (end_row, end_col),
                            self.board
                        )
                    )

                break

    def get_king_capture_moves(self, row, col, moves):

        king_moves = [
            (-1,-1), (-1,0), (-1,1),
            (0,-1),          (0,1),
            (1,-1),  (1,0),  (1,1)
        ]

        ally_color = self.board[row][col][0]

        for dr, dc in king_moves:

            end_row = row + dr
            end_col = col + dc

            if 0 <= end_row < 8 and 0 <= end_col < 8:

                end_piece = self.board[end_row][end_col]

                if end_piece != '--' and end_piece[0] != ally_color:

                    moves.append(
                        Move(
                            (row, col),
                            (end_row, end_col),
                            self.board
                        )
                    )

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

