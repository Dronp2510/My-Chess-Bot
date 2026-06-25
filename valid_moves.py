import pygame

def highlight_moves(surface, valid_moves, board_rect, is_white=True):
    WIDTH, HEIGHT = surface.get_size()
    square_size = board_rect.width // 8

    for move in valid_moves:

        if is_white:
            row = move.end_row
            col = move.end_col
        else:
            row = 7 - move.end_row
            col = 7 - move.end_col

        highlight = pygame.Surface((square_size, square_size))
        highlight.set_alpha(100)
        highlight.fill((0, 0, 255))

        surface.blit(
            highlight,
            (board_rect.x + col * square_size, board_rect.y + row * square_size)
        )