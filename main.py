import pygame
from engine.game_state import GameState
from engine.move import Move
from valid_moves import *

pygame.init()
gs = GameState()

window = pygame.display.set_mode((500,500) , pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption("My Chess")
selected_square = None
valid_moves = []
run = True
colors = [pygame.Color('white') , pygame.Color('brown')]




def chess_board(surface):

    WIDTH , HEIGHT = surface.get_size()
    SQUARE_SIZE = min(WIDTH , HEIGHT) // 8
    for row in range(8):
        for column in range(8):
            color = colors[((row + column) % 2)]
            rect = pygame.Rect(column * SQUARE_SIZE , row * SQUARE_SIZE , SQUARE_SIZE , SQUARE_SIZE)
            pygame.draw.rect(surface , color , rect)
    
    return SQUARE_SIZE

def load_images(square_size):
    pieces = ['wp','wr','wkn','wb','wq','wk',
              'bp','br','bkn','bb','bq','bk']

    images = {}

    for piece in pieces:
        img = pygame.image.load(f"D:/Miscelleneous/VisualStudio/My Chess Bot/My Chess Bot/Assets/{piece}.png").convert_alpha()
        img = pygame.transform.smoothscale(img, (square_size, square_size))
        images[piece] = img

    return images

images = load_images(min(window.get_size()) // 8)

def draw_pieces(surface, board, images, is_white=True):
    WIDTH, HEIGHT = surface.get_size()
    square_size = min(WIDTH, HEIGHT) // 8

    for row in range(8):
        for col in range(8):

            display_row = row if is_white else 7 - row
            display_col = col if is_white else 7 - col

            piece = board[row][col]

            if piece != "--":
                surface.blit(images[piece] , (display_col * square_size, display_row * square_size))


    
def get_all_valid_moves(board, color):
    all_moves = []

    for row in range(8):
        for col in range(8):
            piece = board[row][col]

            if piece != "--" and piece[0] == color:
                moves = get_valid_moves(board, (row, col))
                if moves:
                    all_moves.extend(moves)

    return all_moves

def is_in_check(board, color):
    king_pos = find_king(board, color)
    enemy_color = 'b' if color == 'w' else 'w'

    return is_square_attacked(board, king_pos[0], king_pos[1], enemy_color)

def get_game_state(board, color):
    all_moves = get_all_valid_moves(board, color)

    if len(all_moves) == 0:
        if is_in_check(board, color):
            return "checkmate"
        else:
            return "stalemate"

    return "ongoing"


def get_valid_moves(board , position):
    row , col = position
    piece = board[row][col]

    if piece == '--':
        return []
    
    piece_type = piece[1:]
    color = piece[0]

    if piece_type == 'p':
        moves = get_pawn_move(board , row , col , color , gs.en_passant_square)
    elif piece_type == 'r':
        moves = get_rook_move(board , row , col , color)
    elif piece_type == 'kn':
        moves = get_knight_move(board , row , col , color)
    elif piece_type == 'b':
        moves = get_bishop_move(board , row , col , color)
    elif piece_type == 'k':
        moves = get_king_move(board , row , col , color)
        moves += get_castling_moves(board , row , col , color , gs.castling_rights)
    elif piece_type == 'q':
        moves = get_queen_move(board , row , col , color)
    else:
        moves = []
    
    legal_moves = []

    enemy_color = 'b' if color == 'w' else 'w'

    for end_square in moves:
        move = Move(position, end_square, board)
        temp_board = make_temp_move(board, move)

        king_pos = find_king(temp_board , color)

        if not is_square_attacked(temp_board , king_pos[0] , king_pos[1] , enemy_color):
            legal_moves.append(move)
    
    return legal_moves


# Main Game Loop

while run:
    player_turn = 'w' if gs.white_to_move else 'b'

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            images = load_images(min(window.get_size()) // 8)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            WIDTH, HEIGHT = window.get_size()
            square_size = min(WIDTH, HEIGHT) // 8


            col = mouse_pos[0] // square_size
            row = mouse_pos[1] // square_size
            # print("Clicked:", row, col)
            

            if selected_square is None:
                piece = gs.board[row][col]

                if piece != "--" and piece[0] == player_turn:
                    selected_square = (row, col)
                    valid_moves = get_valid_moves(gs.board , selected_square)
            else:
                piece = gs.board[row][col]
                if piece != '--' and piece[0] == player_turn:
                    selected_square = (row , col)
                    valid_moves = get_valid_moves(gs.board , selected_square)

                move = Move(selected_square, (row, col), gs.board)
                if move in valid_moves:
                    move = Move(selected_square, (row, col), gs.board)
                    gs.make_move(move)
                    state = get_game_state(gs.board, player_turn)

                    if state == "checkmate":
                        print(f"{'White' if player_turn == 'b' else 'Black'} wins by checkmate")

                    elif state == "stalemate":
                        print("Draw by stalemate")

                    player_turn = 'w' if gs.white_to_move else 'b'
                    selected_square = None
                    valid_moves = []
                
                else:
                    selected_square = None
                    valid_moves = []
                    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:

                gs.undo_move()

                selected_square = None
                valid_moves = []
    
    chess_board(window)
    # highlight_square(window, selected_square)
    highlight_moves(window, valid_moves)
    draw_pieces(window , gs.board , images , is_white=True)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()