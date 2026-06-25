import pygame
from pathlib import Path

from engine.game_state import GameState
from engine.move import Move
from valid_moves import highlight_moves
from bots.chess_bot import (
    find_best_move,
    WHITE_BOT_WEIGHTS,
    BLACK_BOT_WEIGHTS,
    clear_search_cache,
)
from bots.bot_profiles import make_weighted_evaluator

pygame.init()

PROJECT_ROOT = Path(__file__).resolve().parent
ASSET_CANDIDATES = [
    PROJECT_ROOT / "Assets",
    PROJECT_ROOT / "assets",
]

# =========================
# Battle UI Layout
# =========================

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

BOARD_SIZE = 760

BOARD_RECT = pygame.Rect(20,20,BOARD_SIZE,BOARD_SIZE)

SIDE_PANEL_X = BOARD_RECT.right + 20
SIDE_PANEL_WIDTH = 520

STATUS_RECT = pygame.Rect(SIDE_PANEL_X,20,SIDE_PANEL_WIDTH,180)
CORRUPTION_RECT = pygame.Rect(SIDE_PANEL_X,220,SIDE_PANEL_WIDTH,180)
INVENTORY_RECT = pygame.Rect(SIDE_PANEL_X,420,SIDE_PANEL_WIDTH,400)
ABILITY_BAR_RECT = pygame.Rect(20,840,1360,60)


def resolve_asset_path(piece_name: str) -> Path:
    for folder in ASSET_CANDIDATES:
        candidate = folder / f"{piece_name}.png"
        if candidate.is_file():
            return candidate

    # Keep a last-resort fallback for older local setups.
    legacy = Path(r"D:/Miscelleneous/VisualStudio/My Chess Bot/My Chess Bot/Assets") / f"{piece_name}.png"
    return legacy

def opponent(color: str) -> str:
    return "b" if color == "w" else "w"

def load_images(square_size):
    pieces = [
        "wp", "wr", "wkn", "wb", "wq", "wk",
        "bp", "br", "bkn", "bb", "bq", "bk",
    ]
    images = {}

    for piece in pieces:
        img = pygame.image.load(str(resolve_asset_path(piece))).convert_alpha()
        img = pygame.transform.smoothscale(img, (square_size, square_size))
        images[piece] = img

    return images

def chess_board(surface, board_rect):

    square_size = board_rect.width // 8

    colors = [pygame.Color("white"), pygame.Color("brown")]
    for row in range(8):
        for column in range(8):
            color = colors[(row + column) % 2]
            rect = pygame.Rect(board_rect.x + column * square_size,board_rect.y + row * square_size,square_size,square_size)
            pygame.draw.rect(surface, color, rect)

    return square_size

def draw_pieces(surface, board, images, board_rect, is_white=True):

    square_size = board_rect.width // 8

    for row in range(8):
        for col in range(8):
            display_row = row if is_white else 7 - row
            display_col = col if is_white else 7 - col
            piece = board[row][col]
            if piece != "--":
                surface.blit(images[piece],(board_rect.x + display_col * square_size,board_rect.y + display_row * square_size))

def current_turn_color(gs):
    return "w" if gs.white_to_move else "b"

def bot_weight_profile(bot_color):
    return WHITE_BOT_WEIGHTS if bot_color == "w" else BLACK_BOT_WEIGHTS

def bot_evaluator(bot_color):
    return make_weighted_evaluator(bot_weight_profile(bot_color))

def draw_battle_panels(surface):

    font = pygame.font.SysFont("arial", 24)

    panels = [(STATUS_RECT, "Status Effects"),(CORRUPTION_RECT, "Corruption"),(INVENTORY_RECT, "Inventory"),(ABILITY_BAR_RECT, "Abilities")]

    for rect, title in panels:
        pygame.draw.rect(surface, (35, 35, 40), rect)
        pygame.draw.rect(surface, (180, 180, 180), rect, 2)
        text = font.render(title, True, (255, 255, 255))
        surface.blit(text,(rect.x + 10, rect.y + 10))


def create_game(player_color="w"):
    gs = GameState()
    return {
        "gs": gs,
        "player_color": player_color,
        "bot_color": opponent(player_color),
        "selected_square": None,
        "valid_moves": [],
    }

state = create_game("w")
gs = state["gs"]
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),pygame.RESIZABLE)
clock = pygame.time.Clock()
pygame.display.set_caption("My Chess")
images = load_images(BOARD_RECT.width // 8)
run = True

def sync_bot_turn():
    global state, gs
    if not run:
        return
    if gs.get_game_state() != "ongoing":
        return

    if current_turn_color(gs) != state["bot_color"]:
        return

    bot_moves = gs.get_all_valid_moves()
    if not bot_moves:
        gs.get_game_state()
        return

    move = find_best_move(
        gs,
        bot_moves,
        evaluator=bot_evaluator(state["bot_color"]),
        quiet=False,
        clear_transposition=True, # make False for training
    )

    if move:
        gs.make_move(move)

    state["selected_square"] = None
    state["valid_moves"] = []

def reset_for_player(player_color: str):
    global state, gs
    clear_search_cache()
    state = create_game(player_color)
    gs = state["gs"]
    sync_bot_turn()


def start_chess_battle(player_color="w"):
    global state, gs

    state = create_game(player_color)
    gs = state["gs"]

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT),pygame.RESIZABLE)
    clock = pygame.time.Clock()
    images = load_images(BOARD_RECT.width // 8)

    sync_bot_turn()

    run = True

    while run:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.VIDEORESIZE:
                window = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE
                )
                images = load_images(
                    min(window.get_size()) // 8
                )

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if gs.get_game_state() != "ongoing":
                    continue

                if current_turn_color(gs) != state["player_color"]:
                    continue

                mouse_pos = pygame.mouse.get_pos()

                square_size = BOARD_RECT.width // 8

                if not BOARD_RECT.collidepoint(mouse_pos):
                    continue

                local_x = mouse_pos[0] - BOARD_RECT.x
                local_y = mouse_pos[1] - BOARD_RECT.y

                raw_col = local_x // square_size
                raw_row = local_y // square_size

                if not (0 <= raw_row < 8 and 0 <= raw_col < 8):
                    continue

                if state["player_color"] == "w":
                    col = raw_col
                    row = raw_row
                else:
                    col = 7 - raw_col
                    row = 7 - raw_row

                if state["selected_square"] is None:

                    piece = gs.board[row][col]

                    if (
                        piece != "--"
                        and piece[0] == state["player_color"]
                    ):
                        state["selected_square"] = (row, col)
                        state["valid_moves"] = gs.get_valid_moves(
                            (row, col)
                        )

                else:

                    piece = gs.board[row][col]

                    if (
                        piece != "--"
                        and piece[0] == state["player_color"]
                    ):
                        state["selected_square"] = (row, col)
                        state["valid_moves"] = gs.get_valid_moves(
                            (row, col)
                        )
                        continue

                    move = Move(
                        state["selected_square"],
                        (row, col),
                        gs.board
                    )

                    if move in state["valid_moves"]:
                        gs.make_move(move)
                        state["selected_square"] = None
                        state["valid_moves"] = []

                    else:
                        state["selected_square"] = None
                        state["valid_moves"] = []

        if gs.get_game_state() == "ongoing":
            sync_bot_turn()

        window.fill((20, 20, 25))
        draw_battle_panels(window)
        chess_board(window,BOARD_RECT)

        is_white_view = (
            state["player_color"] == "w"
        )

        highlight_moves(
            window,
            state["valid_moves"],
            BOARD_RECT,
            is_white=is_white_view
        )

        draw_pieces(
            window,
            gs.board,
            images,
            BOARD_RECT,
            is_white=is_white_view
        )

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    start_chess_battle("w")