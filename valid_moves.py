import pygame

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