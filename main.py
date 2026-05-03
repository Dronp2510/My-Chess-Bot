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

def make_move(board, move):
    (start_row, start_col), (end_row, end_col) = move

    board[end_row][end_col] = board[start_row][start_col]
    board[start_row][start_col] = "--"






def get_valid_moves(board , position):
    row , col = position
    piece = board[row][col]

    if piece == '--':
        return []
    
    piece_type = piece[1:]
    color = piece[0]

    if piece_type == 'p':
        pass
    if piece_type == 'r':
        pass
    if piece_type == 'kn':
        return get_knight_move(board , row , col , color)
    if piece_type == 'b':
        pass
    if piece_type == 'k':
        return get_king_move(board , row , col , color)
    if piece_type == 'q':
        pass
    return []


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
                if (row,col) in valid_moves:
                    move = (selected_square , (row , col))
                    make_move(board , move)

                    player_turn = 'b' if player_turn == 'w' else 'w'
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