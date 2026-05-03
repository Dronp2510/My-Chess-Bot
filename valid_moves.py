import pygame



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





# HIGHLIGHT MOVES.


def highlight_moves(surface, valid_moves):
    WIDTH, HEIGHT = surface.get_size()
    square_size = min(WIDTH, HEIGHT) // 8

    for row, col in valid_moves:
        highlight = pygame.Surface((square_size, square_size))
        highlight.set_alpha(100)
        highlight.fill((0, 0, 255))  # blue

        surface.blit(highlight, (col * square_size, row * square_size))