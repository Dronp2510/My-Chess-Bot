import pygame
from valid_moves import *

pygame.init()


window = pygame.display.set_mode((500,500) , pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption("My Chess")
selected_square = None
valid_moves = []
player_turn = "w"
run = True
colors = [pygame.Color('white') , pygame.Color('brown')]

board = [
    ["br","bkn","bb","bq","bk","bb","bkn","br"],
    ["bp","bp","bp","bp","bp","bp","bp","bp"],
    ["--","--","--","--","--","--","--","--"],
    ["--","--","--","--","--","--","--","--"],
    ["--","--","--","--","--","--","--","--"],
    ["--","--","--","--","--","--","--","--"],
    ["wp","wp","wp","wp","wp","wp","wp","wp"],
    ["wr","wkn","wb","wq","wk","wb","wkn","wr"]
]


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
        img = pygame.image.load(f"D:/Miscelleneous/VisualStudio/My Chess Bot/Assets/{piece}.png").convert_alpha()
        img = pygame.transform.smoothscale(img, (square_size, square_size))
        images[piece] = img

    return images

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

# def make_move(board, move):
#     (start_row, start_col), (end_row, end_col) = move

#     board[end_row][end_col] = board[start_row][start_col]
#     board[start_row][start_col] = "--"

def make_move(board, move):
    (sr, sc), (er, ec) = move
    piece = board[sr][sc]

    board[er][ec] = piece
    board[sr][sc] = "--"

    # update castling rights
    if piece == "wk":
        castling_rights["wks"] = False
        castling_rights["wqs"] = False
    elif piece == "bk":
        castling_rights["bks"] = False
        castling_rights["bqs"] = False

    elif piece == "wr":
        if sr == 7 and sc == 0:
            castling_rights["wqs"] = False
        elif sr == 7 and sc == 7:
            castling_rights["wks"] = False

    elif piece == "br":
        if sr == 0 and sc == 0:
            castling_rights["bqs"] = False
        elif sr == 0 and sc == 7:
            castling_rights["bks"] = False
    # castling move
    if piece[1:] == "k":
        if abs(sc - ec) == 2:
            # king-side
            if ec == 6:
                board[er][5] = board[er][7]
                board[er][7] = "--"
            # queen-side
            elif ec == 2:
                board[er][3] = board[er][0]
                board[er][0] = "--"
    
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
        moves = get_pawn_move(board , row , col , color)
    elif piece_type == 'r':
        moves = get_rook_move(board , row , col , color)
    elif piece_type == 'kn':
        moves = get_knight_move(board , row , col , color)
    elif piece_type == 'b':
        moves = get_bishop_move(board , row , col , color)
    elif piece_type == 'k':
        moves = get_king_move(board , row , col , color)
        moves += get_castling_moves(board , row , col , color)
    elif piece_type == 'q':
        moves = get_queen_move(board , row , col , color)
    else:
        moves = []
    
    legal_moves = []

    enemy_color = 'b' if color == 'w' else 'w'

    for move in moves:
        temp_board = make_temp_move(board , (position , move))

        king_pos = find_king(temp_board , color)

        if not is_square_attacked(temp_board , king_pos[0] , king_pos[1] , enemy_color):
            legal_moves.append(move)
    
    return legal_moves


# Main Game Loop

while run:

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
                piece = board[row][col]

                if piece != "--" and piece[0] == player_turn:
                    selected_square = (row, col)
                    valid_moves = get_valid_moves(board , selected_square)
            else:
                piece = board[row][col]
                if piece != '--' and piece[0] == player_turn:
                    selected_square = (row , col)
                    valid_moves = get_valid_moves(board , selected_square)
                
                elif (row , col) in valid_moves:
                    move = (selected_square , (row , col))
                    make_move(board , move)
                    state = get_game_state(board, player_turn)

                    if state == "checkmate":
                        print(f"{'White' if player_turn == 'b' else 'Black'} wins by checkmate")

                    elif state == "stalemate":
                        print("Draw by stalemate")

                    player_turn = 'b' if player_turn == 'w' else 'w'
                    selected_square = None
                    valid_moves = []
                
                else:
                    selected_square = None
                    valid_moves = []
    
    images = load_images(min(window.get_size()) // 8)
    
    chess_board(window)
    # highlight_square(window, selected_square)
    highlight_moves(window, valid_moves)
    draw_pieces(window , board , images , is_white=True)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()