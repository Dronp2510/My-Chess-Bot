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
from game.battle_state import BattleState
from game.paths.fortune_path import FortunePath
from game.paths.fortune_abilities import (
    LuckyOne,
)

pygame.init()

PROJECT_ROOT = Path(__file__).resolve().parent
ASSET_CANDIDATES = [
    PROJECT_ROOT / "Assets",
    PROJECT_ROOT / "assets",
]

TEMP_ABILITIES = [
    "Lucky One"
]

ABILITY_OBJECTS = {
    "Lucky One": LuckyOne(),
}

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
ABILITY_BAR_RECT = pygame.Rect(20,780,1360,60)

def draw_ability_panel(surface):

    font = pygame.font.SysFont("arial", 22)

    pygame.draw.rect(surface,(35,35,40),ABILITY_BAR_RECT)

    pygame.draw.rect(surface,(180,180,180),ABILITY_BAR_RECT,2)

    title = font.render("Abilities",True,(255,255,255))

    surface.blit(title,(ABILITY_BAR_RECT.x + 10,ABILITY_BAR_RECT.y + 5))

    state["ability_buttons"] = []

    button_width = 160
    button_height = 45

    start_x = ABILITY_BAR_RECT.x + 120
    start_y = ABILITY_BAR_RECT.y + 18

    for i, ability in enumerate(TEMP_ABILITIES):

        rect = pygame.Rect(start_x + i * 150,start_y,button_width,button_height)

        color = ((120,80,20) if state["selected_ability"] == ability else (60,60,70))

        pygame.draw.rect(surface,color,rect,border_radius=5)

        pygame.draw.rect(surface,(200,200,200),rect,2,border_radius=5)

        text = font.render(ability,True,(255,255,255))

        surface.blit(text,text.get_rect(center=rect.center))

        state["ability_buttons"].append({"ability": ability,"rect": rect})
        
    battle_state = state["battle_state"]

    cz_text = font.render(
        f"CZ: {battle_state.cz.current_cz} / {battle_state.cz.max_cz}",
        True,
        (255,215,0)
    )

    if state["ability_targeting"]:
        target_text = font.render(f"TARGETING: {state['selected_ability']}",True,(255,220,0))
        surface.blit(target_text,(ABILITY_BAR_RECT.x + 400,ABILITY_BAR_RECT.y + 15))
    
    surface.blit(cz_text,(ABILITY_BAR_RECT.right - 120,ABILITY_BAR_RECT.y + 15))


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
    
    battle_state = state["battle_state"]
    for square, effects in battle_state.statuses.items():
        row, col = square
        display_row = row if is_white else 7 - row
        display_col = col if is_white else 7 - col

        center = (board_rect.x + display_col * square_size + square_size // 2,board_rect.y + display_row * square_size + square_size // 2)

        for effect in effects:
            if effect.name == "Fortunate":
                pygame.draw.circle(surface,(255,215,0),center,square_size // 4,4)

def current_turn_color(gs):
    return "w" if gs.white_to_move else "b"

def bot_weight_profile(bot_color):
    return WHITE_BOT_WEIGHTS if bot_color == "w" else BLACK_BOT_WEIGHTS

def bot_evaluator(bot_color):
    return make_weighted_evaluator(bot_weight_profile(bot_color))

def draw_battle_panels(surface):

    font = pygame.font.SysFont("arial", 24)

    panels = [(STATUS_RECT, "Status Effects"),(CORRUPTION_RECT, "Corruption"),(INVENTORY_RECT, "Inventory")]

    for rect, title in panels:
        pygame.draw.rect(surface, (35, 35, 40), rect)
        pygame.draw.rect(surface, (180, 180, 180), rect, 2)
        text = font.render(title, True, (255, 255, 255))
        surface.blit(text,(rect.x + 10, rect.y + 10))

    battle_state = state["battle_state"]
    y = STATUS_RECT.y + 50

    for square, effects in battle_state.statuses.items():
        names = ", ".join(effect.name for effect in effects)
        text = font.render(f"{square}: {names}",True,(220,220,220))
        surface.blit(text,(STATUS_RECT.x + 10, y))
        y += 25


def create_game(player_color="w"):
    gs = GameState()
    battle_state = BattleState(FortunePath(stage=5))
    return {
        "gs": gs,
        "battle_state": battle_state,
        "player_color": player_color,
        "bot_color": opponent(player_color),
        "selected_square": None,
        "valid_moves": [],
        "selected_ability": None,
        "ability_buttons": [],
        "ability_targeting": False,
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

                ability_clicked = False

                for button in state["ability_buttons"]:

                    if button["rect"].collidepoint(mouse_pos):
                        state["selected_ability"] = button["ability"]
                        state["ability_targeting"] = True

                        state["selected_square"] = None
                        state["valid_moves"] = []
                        ability_clicked = True
                        break

                if ability_clicked:
                    continue

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

                if state["ability_targeting"]:

                    piece = gs.board[row][col]

                    if (piece != "--"and piece[0] == state["player_color"]):

                        ability = ABILITY_OBJECTS[state["selected_ability"]]

                        success = ability.activate(state["battle_state"],targets=[(row, col)],owner_color=state["player_color"])

                        if success:
                            state["ability_targeting"] = False
                            state["selected_ability"] = None

                        state["selected_square"] = None
                        state["valid_moves"] = []

                    continue

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

                        state["battle_state"].move_piece_status((move.start_row, move.start_col),(move.end_row, move.end_col))

                        if move.is_castle_move:
                            if move.end_col == 6:
                                state["battle_state"].move_piece_status((move.start_row, 7),(move.start_row, 5))

                            else:
                                state["battle_state"].move_piece_status((move.start_row, 0),(move.start_row, 3))

                        gs.make_move(move)
                        state["selected_square"] = None
                        state["valid_moves"] = []

        if gs.get_game_state() == "ongoing":
            sync_bot_turn()

        window.fill((20, 20, 25))
        draw_battle_panels(window)
        draw_ability_panel(window)
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