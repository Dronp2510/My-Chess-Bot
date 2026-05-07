import pygame

def find_king(board, color):
    for row in range(8):
        for col in range(8):
            if board[row][col] == f"{color}k":
                return (row, col)
    return None

def is_square_attacked(board, row, col, enemy_color):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]

            if piece != "--" and piece[0] == enemy_color:
                piece_type = piece[1:]

                if piece_type == 'p':
                    direction = -1 if enemy_color == 'w' else 1

                    attack_squares = []
                    if 0 <= r + direction < 8:
                        if 0 <= c - 1 < 8:
                            attack_squares.append((r + direction, c - 1))
                        if 0 <= c + 1 < 8:
                            attack_squares.append((r + direction, c + 1))
                    moves = attack_squares

                elif piece_type == 'r':
                    moves = get_rook_move(board, r, c, enemy_color)

                elif piece_type == 'kn':
                    moves = get_knight_move(board, r, c, enemy_color)

                elif piece_type == 'b':
                    moves = get_bishop_move(board, r, c, enemy_color)

                elif piece_type == 'q':
                    moves = get_queen_move(board, r, c, enemy_color)

                elif piece_type == 'k':
                    moves = get_king_move(board, r, c, enemy_color)

                if (row, col) in moves:
                    return True

    return False

def loop_function(board , row , col , color , directions):
    moves = []

    for dr, dc in directions:
        for i in range(1, 8):  # max 7 steps

            new_row = row + dr * i
            new_col = col + dc * i

            # stop if out of board
            if not (0 <= new_row < 8 and 0 <= new_col < 8):
                break

            target = board[new_row][new_col]

            # empty square → valid move
            if target == "--":
                moves.append((new_row, new_col))

            else:
                # enemy piece → capture allowed, then stop
                if target[0] != color:
                    moves.append((new_row, new_col))

                # friendly or enemy → cannot go beyond
                break

    return moves

def get_king_move(board , row , col , color):
    moves = []
    king_moves = [
        (1,1) , (1,-1) , (-1,1) , (-1,-1) , (0,1) , (0,-1) , (1,0) , (-1,0)
    ]

    for dr , dc in king_moves:
        new_row = row + dr
        new_col = col + dc

        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target = board[new_row][new_col]

            if target == '--' or target[0] != color:
                moves.append((new_row , new_col))
    return moves

def get_castling_moves(board, row, col, color, castling_rights):

    moves = []
    enemy = 'b' if color == 'w' else 'w'

    if board[row][col] != f"{color}k":
        return moves

    # king cannot castle while in check
    if is_square_attacked(board, row, col, enemy):
        return moves

    # =========================
    # WHITE CASTLING
    # =========================

    if color == "w":

        # king-side
        if castling_rights["wks"]:

            if board[7][5] == "--" and board[7][6] == "--":

                if not is_square_attacked(board, 7, 5, enemy) and \
                   not is_square_attacked(board, 7, 6, enemy):

                    moves.append((7, 6))

        # queen-side
        if castling_rights["wqs"]:

            if board[7][1] == "--" and \
               board[7][2] == "--" and \
               board[7][3] == "--":

                if not is_square_attacked(board, 7, 2, enemy) and \
                   not is_square_attacked(board, 7, 3, enemy):

                    moves.append((7, 2))

    # =========================
    # BLACK CASTLING
    # =========================

    else:

        # king-side
        if castling_rights["bks"]:

            if board[0][5] == "--" and board[0][6] == "--":

                if not is_square_attacked(board, 0, 5, enemy) and \
                   not is_square_attacked(board, 0, 6, enemy):

                    moves.append((0, 6))

        # queen-side
        if castling_rights["bqs"]:

            if board[0][1] == "--" and \
               board[0][2] == "--" and \
               board[0][3] == "--":

                if not is_square_attacked(board, 0, 2, enemy) and \
                   not is_square_attacked(board, 0, 3, enemy):

                    moves.append((0, 2))

    return moves

def get_queen_move(board , row , col , color):
    queen_moves_direction = [
        (0,1) , (0,-1) , (1,0) , (-1,0) ,
        (1,1) , (1,-1) , (-1,1) , (-1,-1)
    ]

    return loop_function(board , row , col , color , queen_moves_direction)

def get_rook_move(board , row , col , color):
    rook_moves_direction = [
        (0 , 1) , (0 , -1) , 
        (1 , 0) , (-1 , 0)
    ]

    return loop_function(board , row , col , color , rook_moves_direction)

def get_bishop_move(board , row , col , color):
    bishop_moves_direction = [
        (1 , 1) , (1 , -1) ,
        (-1 , 1) , (-1 , -1)
    ]

    return loop_function(board , row , col , color , bishop_moves_direction)

def get_knight_move(board , row , col , color):
    moves = []
    knight_moves = [
        (2,1) , (2,-1) ,
        (-2,1) , (-2,-1) ,
        (1,2) , (1,-2) ,
        (-1,2) , (-1,-2)
    ]

    for dr , dc in knight_moves:
        new_row = row + dr
        new_col = col + dc

        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target = board[new_row][new_col]

            if target == '--' or target[0] != color:
                moves.append((new_row , new_col))

    return moves

def get_pawn_move(board , row , col , color):
    moves = []
    direction = -1 if color == 'w' else 1
    start_row = 6 if color == 'w' else 1
    if 0 <= row + direction < 8 and board[row + direction][col] == '--':
        moves.append((row + direction , col))

        if row == start_row and board[row + 2 * direction][col] == '--':
            moves.append((row + 2 * direction , col)) 
    
    # Capture left
    if 0 <= col - 1 < 8 and 0 <= row + direction < 8:
        target = board[row + direction][col - 1]
        if target != '--' and target[0] != color:
            moves.append((row + direction , col - 1))

    # Capture right
    if 0 <= col + 1 < 8 and 0 <= row + direction < 8:
        target = board[row + direction][col + 1]
        if target != '--' and target[0] != color:
            moves.append((row + direction , col + 1))
    
    return moves

def make_temp_move(board, move):
    new_board = [row[:] for row in board]

    sr = move.start_row
    sc = move.start_col

    er = move.end_row
    ec = move.end_col

    new_board[er][ec] = new_board[sr][sc]
    new_board[sr][sc] = "--"

    return new_board

# HIGHLIGHT MOVES.


def highlight_moves(surface, valid_moves):
    WIDTH, HEIGHT = surface.get_size()
    square_size = min(WIDTH, HEIGHT) // 8

    for move in valid_moves:
        row = move.end_row
        col = move.end_col
        highlight = pygame.Surface((square_size, square_size))
        highlight.set_alpha(100)
        highlight.fill((0, 0, 255))  # blue

        surface.blit(highlight, (col * square_size, row * square_size))