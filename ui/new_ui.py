"""Small, self-contained campaign UI for the chess roguelike.

The screen flow intentionally lives in one module so it is easy to run from
the repository root without introducing a second framework or dependency.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pygame

# Allow this module to be launched directly as `python ui\new_ui.py` while
# keeping imports unchanged when it is imported by the repository entry point.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bots.bot_profiles import make_weighted_evaluator
from bots.chess_bot import (
    BLACK_BOT_WEIGHTS,
    WHITE_BOT_WEIGHTS,
    clear_search_cache,
    find_best_move,
)
from engine.game_state import GameState
from engine.move import Move
from game.battle_state import BattleState
from game.paths.fortune_path import FortunePath
from game.status_processors import apply_misfortunate_filter
from game.status_effects import MisfortunateStatus


BG = (12, 16, 29)
PANEL = (24, 31, 50)
PANEL_LIGHT = (35, 45, 70)
GOLD = (242, 190, 76)
TEXT = (235, 239, 247)
MUTED = (150, 164, 190)
ACCENT = (90, 185, 190)


class CampaignUI:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((1180, 760), pygame.RESIZABLE)
        pygame.display.set_caption("Chess: Fortune's Path")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 26)
        self.small = pygame.font.Font(None, 20)
        self.title = pygame.font.Font(None, 64)
        self.running = True
        self.mode = "menu"
        self.hover = None
        self.map_nodes = [
            (180, 570, "Scout", "Easy"),
            (340, 450, "Duel", "Medium"),
            (500, 560, "Ambush", "Hard"),
            (620, 330, "Elite", "Hard"),
            (790, 440, "Champion", "Expert"),
            (950, 270, "The Spire", "Boss"),
        ]
        self.reached = 0
        self.gs = None
        self.battle = None
        self.player_color = "w"
        self.selected = None
        self.valid_moves = []
        self.images = {}
        self.abilities = []
        self.selected_ability = None
        self.hover_square = None

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            if self.mode == "battle":
                self._bot_turn()
            self.draw(dt)
        pygame.quit()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        elif event.type == pygame.MOUSEMOTION:
            self.hover = event.pos
            self.hover_square = self._board_square_at(event.pos) if self.mode == "battle" else None
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.mode = "map" if self.mode == "battle" else "menu"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.mode == "menu":
                if self._button_rect().collidepoint(event.pos):
                    self.mode = "map"
            elif self.mode == "map":
                self._map_click(event.pos)
            elif self.mode == "battle":
                self._board_click(event.pos)

    def draw(self, _dt: float) -> None:
        self.screen.fill(BG)
        if self.mode == "menu":
            self._draw_menu()
        elif self.mode == "map":
            self._draw_map()
        else:
            self._draw_battle()
        pygame.display.flip()

    def _draw_menu(self) -> None:
        w, h = self.screen.get_size()
        for y in range(h):
            shade = int(16 + 18 * y / max(h, 1))
            pygame.draw.line(self.screen, (10, shade // 2, shade), (0, y), (w, y))
        self._text("FORTUNE'S PATH", (76, 125), self.title, GOLD)
        self._text("A chess roguelike of calculated risks", (80, 190), self.font, MUTED)
        pygame.draw.circle(self.screen, (35, 67, 86), (int(w * .72), h // 2), 170)
        pygame.draw.circle(self.screen, (16, 28, 44), (int(w * .72), h // 2), 125)
        self._text("♔", (int(w * .72) - 42, h // 2 - 56), pygame.font.Font(None, 110), GOLD)
        rect = self._button_rect()
        pygame.draw.rect(self.screen, ACCENT, rect, border_radius=8)
        self._text("BEGIN ASCENT", (rect.centerx, rect.centery), self.font, BG, center=True)
        self._text("Click to start  •  ESC to return", (80, rect.bottom + 28), self.small, MUTED)

    def _button_rect(self) -> pygame.Rect:
        return pygame.Rect(80, 290, 230, 54)

    def _draw_map(self) -> None:
        self._header("THE ASCENT", "Choose your next encounter")
        pygame.draw.rect(self.screen, PANEL, (45, 105, self.screen.get_width() - 90, 570), border_radius=14)
        for a, b in zip(self.map_nodes, self.map_nodes[1:]):
            pygame.draw.line(self.screen, (70, 91, 116), (a[0], a[1]), (b[0], b[1]), 4)
        for index, (x, y, name, difficulty) in enumerate(self.map_nodes):
            unlocked = index <= self.reached + 1
            color = GOLD if index == self.reached else (ACCENT if unlocked else (65, 73, 91))
            pygame.draw.circle(self.screen, (13, 20, 34), (x, y), 34)
            pygame.draw.circle(self.screen, color, (x, y), 29, 4)
            self._text(str(index + 1), (x, y), self.font, color, center=True)
            self._text(name, (x, y + 46), self.small, TEXT if unlocked else MUTED, center=True)
            self._text(difficulty, (x, y + 66), self.small, MUTED, center=True)
        self._text("Select a node to begin a chess battle", (60, 700), self.small, MUTED)

    def _draw_battle(self) -> None:
        self._header("CHESS BATTLE", "Your turn" if self._player_turn() else "Opponent thinking…")
        board_size = min(self.screen.get_height() - 150, 570)
        board = pygame.Rect(55, 115, board_size, board_size)
        sq = board_size // 8
        for row in range(8):
            for col in range(8):
                color = (224, 213, 184) if (row + col) % 2 == 0 else (94, 128, 133)
                pygame.draw.rect(self.screen, color, (board.x + col * sq, board.y + row * sq, sq, sq))
        self._draw_status_glows(board, sq)
        self._draw_hover_preview(board, sq)
        if self.selected:
            r, c = self.selected
            pygame.draw.rect(self.screen, (246, 214, 91), (board.x + c * sq, board.y + r * sq, sq, sq), 4)
        for move in self.valid_moves:
            color = (210, 92, 76) if move.piece_captured != "--" else (40, 95, 90)
            pygame.draw.circle(self.screen, color, (board.x + move.end_col * sq + sq // 2, board.y + move.end_row * sq + sq // 2), 8)
        for row, pieces in enumerate(self.gs.board):
            for col, piece in enumerate(pieces):
                if piece != "--":
                    self._draw_piece(piece, board.x + col * sq, board.y + row * sq, sq)
        x = board.right + 35
        pygame.draw.rect(self.screen, PANEL, (x, 115, self.screen.get_width() - x - 45, board_size), border_radius=12)
        self._text("FORTUNE'S PATH", (x + 24, 145), self.font, GOLD)
        self._text("White  •  You", (x + 24, 195), self.small, TEXT)
        self._text("Black  •  The House", (x + 24, 222), self.small, MUTED)
        instruction = (
            f"Targeting {self.selected_ability.name}"
            if self.selected_ability
            else "Click a piece, then a highlighted square."
        )
        self._text(instruction, (x + 24, 285), self.small, GOLD if self.selected_ability else MUTED)
        self._draw_ability_panel(x, board)
        status = self.gs.get_game_state()
        if status != "ongoing":
            self._text(status.upper(), (x + 24, 355), self.font, GOLD)
            self._text("Click MAP or press ESC", (x + 24, 390), self.small, MUTED)
        self._text("ESC  Back to map", (x + 24, board.bottom - 35), self.small, MUTED)

    def _draw_ability_panel(self, x: int, board: pygame.Rect) -> None:
        panel_width = self.screen.get_width() - x - 45
        top = 325
        self._text("ABILITIES", (x + 24, top), self.small, GOLD)
        cz = self.battle.cz
        self._text(f"CZ  {cz.current_cz} / {cz.max_cz}", (x + panel_width - 125, top), self.small, TEXT)

        for index, ability in enumerate(self.abilities):
            rect = pygame.Rect(x + 24, top + 32 + index * 52, panel_width - 48, 42)
            affordable = cz.can_afford(ability.cost)
            selected = self.selected_ability is ability
            fill = (116, 82, 35) if selected else (42, 58, 78) if affordable else (34, 40, 55)
            label_color = TEXT if affordable else MUTED
            pygame.draw.rect(self.screen, fill, rect, border_radius=6)
            pygame.draw.rect(self.screen, GOLD if selected else (76, 96, 120), rect, 2, border_radius=6)
            self._text(ability.name, (rect.x + 12, rect.centery), self.small, label_color)
            self._text(f"{ability.cost} CZ", (rect.right - 58, rect.centery), self.small, label_color, center=True)

    def _draw_status_glows(self, board: pygame.Rect, sq: int) -> None:
        for (row, col), effects in self.battle.statuses.items():
            for effect in effects:
                color = GOLD if effect.name == "Fortunate" else (190, 92, 210)
                center = (board.x + col * sq + sq // 2, board.y + row * sq + sq // 2)
                pygame.draw.circle(self.screen, color, center, max(12, sq // 3), 4)
                glow_color = tuple(min(255, channel // 2 + 20) for channel in color)
                pygame.draw.circle(self.screen, glow_color, center, max(15, sq // 2 - 4), 2)

    def _draw_hover_preview(self, board: pygame.Rect, sq: int) -> None:
        if self.hover_square is None:
            return
        row, col = self.hover_square
        piece = self.gs.board[row][col]
        if piece == "--":
            return

        if self.selected and any(
            move.end_row == row and move.end_col == col for move in self.valid_moves
        ):
            pygame.draw.rect(
                self.screen,
                (220, 86, 70),
                (board.x + col * sq, board.y + row * sq, sq, sq),
                4,
            )
            return

        pygame.draw.rect(
            self.screen,
            GOLD if self.selected_ability is None else ACCENT,
            (board.x + col * sq, board.y + row * sq, sq, sq),
            3,
        )

        if self.selected_ability is not None:
            if not self.selected_ability.validate_target(
                self.gs, self.battle, self.hover_square, self.player_color
            ):
                return
            if self.selected_ability.name == "Unlucky One":
                moves, reduced = self._misfortune_preview(self.hover_square)
                self._draw_preview_moves(board, sq, moves, (70, 150, 190))
                self._draw_preview_moves(board, sq, reduced, (185, 76, 76))
            return

        if piece[0] == self.player_color and self._player_turn():
            moves = self.gs.get_valid_moves(self.hover_square)
            self._draw_preview_moves(board, sq, moves, None)

    def _draw_preview_moves(self, board: pygame.Rect, sq: int, moves, color) -> None:
        for move in moves:
            marker_color = color or ((210, 92, 76) if move.piece_captured != "--" else (40, 95, 90))
            center = (
                board.x + move.end_col * sq + sq // 2,
                board.y + move.end_row * sq + sq // 2,
            )
            pygame.draw.circle(self.screen, marker_color, center, 9 if color else 7)

    def _misfortune_preview(self, square):
        moves = self.gs.get_valid_moves(square)
        status = self.battle.get_status(square, "Misfortunate")
        if status is None:
            status = MisfortunateStatus(
                owner_color=self.player_color,
                reduction_percent=self.battle.path.get_move_reduction(),
                duration=1,
                seed=(square[0] * 8 + square[1]),
            )
        return moves, apply_misfortunate_filter(moves, status)

    def _board_square_at(self, pos):
        board_size = min(self.screen.get_height() - 150, 570)
        board = pygame.Rect(55, 115, board_size, board_size)
        if not board.collidepoint(pos):
            return None
        sq = board_size // 8
        return ((pos[1] - board.y) // sq, (pos[0] - board.x) // sq)

    def _header(self, heading: str, subtitle: str) -> None:
        self._text(heading, (45, 38), self.font, GOLD)
        self._text(subtitle, (45, 68), self.small, MUTED)

    def _text(self, value, pos, font, color, center=False) -> None:
        image = font.render(str(value), True, color)
        rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
        self.screen.blit(image, rect)

    def _map_click(self, pos) -> None:
        for index, (x, y, *_rest) in enumerate(self.map_nodes):
            if index <= self.reached + 1 and (pos[0] - x) ** 2 + (pos[1] - y) ** 2 < 40 ** 2:
                self.reached = max(self.reached, index)
                self._start_battle()
                return

    def _start_battle(self) -> None:
        clear_search_cache()
        self.gs = GameState()
        self.battle = BattleState(FortunePath(stage=5))
        self.gs.battle_state = self.battle
        self.abilities = self.battle.path.get_abilities()
        self.player_color = "w"
        self.selected = None
        self.valid_moves = []
        self.selected_ability = None
        self.hover_square = None
        self.mode = "battle"

    def _player_turn(self) -> bool:
        return self.gs is not None and self.gs.white_to_move == (self.player_color == "w")

    def _board_click(self, pos) -> None:
        board_size = min(self.screen.get_height() - 150, 570)
        board = pygame.Rect(55, 115, board_size, board_size)
        if not self._player_turn() or self.gs.get_game_state() != "ongoing":
            return
        x = board.right + 35
        panel_width = self.screen.get_width() - x - 45
        for index, ability in enumerate(self.abilities):
            rect = pygame.Rect(x + 24, 357 + index * 52, panel_width - 48, 42)
            if rect.collidepoint(pos):
                self.selected_ability = None if self.selected_ability is ability else ability
                self.selected = None
                self.valid_moves = []
                return
        if not board.collidepoint(pos):
            return
        sq = board_size // 8
        row, col = (pos[1] - board.y) // sq, (pos[0] - board.x) // sq
        piece = self.gs.board[row][col]
        if self.selected_ability is not None:
            if self.selected_ability.validate_target(
                self.gs, self.battle, (row, col), self.player_color
            ):
                activated = self.selected_ability.activate(
                    self.battle,
                    targets=[(row, col)],
                    owner_color=self.player_color,
                )
                if activated:
                    self.gs.recompute_status_hash()
                    self.selected_ability = None
            return
        if self.selected is None:
            if piece != "--" and piece[0] == self.player_color:
                self.selected = (row, col)
                self.valid_moves = self.gs.get_valid_moves(self.selected)
            return
        if piece != "--" and piece[0] == self.player_color:
            self.selected = (row, col)
            self.valid_moves = self.gs.get_valid_moves(self.selected)
            return
        move = Move(self.selected, (row, col), self.gs.board)
        if move in self.valid_moves:
            self.gs.make_move(move)
        self.selected = None
        self.valid_moves = []

    def _bot_turn(self) -> None:
        if self.gs is None or self._player_turn() or self.gs.get_game_state() != "ongoing":
            return
        moves = self.gs.get_all_valid_moves()
        if not moves:
            return
        weights = WHITE_BOT_WEIGHTS if self.player_color == "b" else BLACK_BOT_WEIGHTS
        move = find_best_move(self.gs, moves, evaluator=make_weighted_evaluator(weights), quiet=True, clear_transposition=True)
        if move:
            self.gs.make_move(move)

    def _draw_piece(self, piece: str, x: int, y: int, size: int) -> None:
        path = ROOT / "Assets" / "Classic" / f"{piece}.png"
        if path.is_file():
            image = pygame.image.load(str(path)).convert_alpha()
            image = pygame.transform.smoothscale(image, (size, size))
            self.screen.blit(image, (x, y))
        else:
            glyph = {"p": "♟", "r": "♜", "kn": "♞", "b": "♝", "q": "♛", "k": "♚"}[piece[1:]]
            self._text(glyph, (x + size // 2, y + size // 2), pygame.font.Font(None, size - 8), (20, 20, 25) if piece[0] == "b" else (250, 250, 240), center=True)


def run() -> None:
    CampaignUI().run()


if __name__ == "__main__":
    run()
