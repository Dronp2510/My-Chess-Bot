import pygame
import math
import sys
from pathlib import Path

# --- Path Configuration ---
# Assuming this file is in ProjectRoot/UI/ui_main.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSET_CANDIDATES = [
    PROJECT_ROOT / "Assets",
    PROJECT_ROOT / "assets",
]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import start_chess_battle
import random

def resolve_asset_path(piece_name: str) -> Path:
    for folder in ASSET_CANDIDATES:
        candidate = folder / f"{piece_name}.png"
        if candidate.is_file():
            return candidate
    return None

# --- Constants & Colors ---
WIDTH, HEIGHT = 1024, 768
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
PURPLE = (80, 0, 120)
GOLD = (255, 215, 0)
RED = (200, 50, 50)

# --- Helper Classes ---

class Button:
    def __init__(self, x, y, width, height, text, font, action=None, color=DARK_GRAY, hover_color=GRAY, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=5)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()

class OrbitingPiece:
    def __init__(self, image, distance, speed, start_angle):
        self.image = image
        self.distance = distance
        self.speed = speed
        self.angle = start_angle

    def update(self):
        self.angle += self.speed
        if self.angle >= 360:
            self.angle -= 360

    def draw(self, surface, center_x, center_y):
        # Convert angle to radians for math functions
        rad = math.radians(self.angle)
        x = center_x + math.cos(rad) * self.distance
        y = center_y + math.sin(rad) * self.distance
        
        rect = self.image.get_rect(center=(int(x), int(y)))
        surface.blit(self.image, rect)

# --- Main App Class ---

class GameApp:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess: Outer Gods")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("impact", 72)
        self.font_button = pygame.font.SysFont("arial", 32)
        self.font_text = pygame.font.SysFont("arial", 24)

        # Game Settings
        self.sound_enabled = True
        self.piece_preference = "Any" # "White" (Easy), "Any" (Moderate), "Black" (Hard)
        
        # State Machine: MAIN_MENU, OPTIONS, PATH_SELECT, MAP
        self.state = "MAIN_MENU"

        # Load Visuals
        self.load_orbiting_pieces()
        self.load_difficulty_icons()
        self.init_ui()

    def load_orbiting_pieces(self):
        self.orbiters = []
        pieces_to_load = ["wp", "wkn", "wb", "wr", "wq", "wk", "bp", "bk"]
        
        distance = 150
        angle_step = 360 / len(pieces_to_load)
        
        for i, p_name in enumerate(pieces_to_load):
            path = resolve_asset_path(p_name)
            img = None
            if path:
                try:
                    img = pygame.image.load(str(path)).convert_alpha()
                    img = pygame.transform.smoothscale(img, (50, 50))
                except Exception:
                    pass
            
            # Fallback if image fails to load
            if not img:
                img = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(img, WHITE if p_name.startswith('w') else GRAY, (20, 20), 20)

            speed = 1.0 if i % 2 == 0 else 1.5 # Varying speeds
            self.orbiters.append(OrbitingPiece(img, distance + (i % 3 * 20), speed, i * angle_step))
    
    def load_difficulty_icons(self):
        self.easy_icon = None
        self.moderate_icon = None
        self.hard_icon = None

        try:
            self.easy_icon = pygame.transform.smoothscale(
                pygame.image.load(
                    str(resolve_asset_path("wk"))
                ).convert_alpha(),
                (80, 80)
            )
        except:
            pass

        try:
            white = pygame.image.load(
                str(resolve_asset_path("wk"))
            ).convert_alpha()

            black = pygame.image.load(
                str(resolve_asset_path("bk"))
            ).convert_alpha()

            white = pygame.transform.smoothscale(white, (80, 80))
            black = pygame.transform.smoothscale(black, (80, 80))

            moderate = pygame.Surface(
                (80, 80),
                pygame.SRCALPHA
            )

            moderate.blit(
                white,
                (0, 0),
                pygame.Rect(0, 0, 40, 80)
            )

            moderate.blit(
                black,
                (40, 0),
                pygame.Rect(40, 0, 40, 80)
            )

            self.moderate_icon = moderate

        except:
            pass

        try:
            self.hard_icon = pygame.transform.smoothscale(
                pygame.image.load(
                    str(resolve_asset_path("bk"))
                ).convert_alpha(),
                (80, 80)
            )
        except:
            pass

    def init_ui(self):
        btn_w, btn_h = 250, 60
        left_center_x = WIDTH * 0.25 - (btn_w // 2)
        start_y = HEIGHT // 2 - 50
        gap = 80

        # --- Main Menu Buttons ---
        self.btn_play = Button(left_center_x, start_y, btn_w, btn_h, "Play", self.font_button, lambda: self.change_state("DIFFICULTY_SELECT"))
        self.btn_options = Button(left_center_x, start_y + gap, btn_w, btn_h, "Options", self.font_button, lambda: self.change_state("OPTIONS"))
        self.btn_quit = Button(left_center_x, start_y + gap * 2, btn_w, btn_h, "Quit", self.font_button, self.quit_game)
        self.main_buttons = [self.btn_play, self.btn_options, self.btn_quit]

        # --- Difficulty ---
        self.easy_rect = pygame.Rect(100, 180, 220, 320)
        self.moderate_rect = pygame.Rect(400, 180, 220, 320)
        self.hard_rect = pygame.Rect(700, 180, 220, 320)
        self.btn_diff_back = Button(WIDTH//2 - 125,600,250,50,"Back",self.font_button,lambda: self.change_state("MAIN_MENU"))

        # --- Path Select Buttons ---
        center_x = WIDTH // 2 - (btn_w // 2)
        self.btn_path_1 = Button(center_x, 250, btn_w, btn_h, "Path of the Void", self.font_button, lambda: self.select_path("Void"))
        self.btn_path_2 = Button(center_x, 350, btn_w, btn_h, "Path of the Stars", self.font_button, lambda: self.select_path("Stars"))
        self.btn_path_3 = Button(center_x, 450, btn_w, btn_h, "Path of the Old Blood", self.font_button, lambda: self.select_path("Old Blood"))
        self.btn_path_back = Button(center_x, 600, btn_w, btn_h, "Back", self.font_button, lambda: self.change_state("MAIN_MENU"))
        self.path_buttons = [self.btn_path_1, self.btn_path_2, self.btn_path_3, self.btn_path_back]

        # --- Options Buttons ---
        self.btn_toggle_sound = Button(center_x, 250, btn_w, btn_h, f"Sound: ON", self.font_button, self.toggle_sound)
        self.btn_opt_back = Button(center_x, 500, btn_w, btn_h, "Back", self.font_button, lambda: self.change_state("MAIN_MENU"))
        self.opt_buttons = [self.btn_toggle_sound, self.btn_opt_back]


    def change_state(self, new_state):
        self.state = new_state


    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        status = "ON" if self.sound_enabled else "OFF"
        self.btn_toggle_sound.text = f"Sound: {status}"

    def start_difficulty(self, difficulty):


        if difficulty == "easy":
            player_color = "w"

        elif difficulty == "hard":
            player_color = "b"

        else:
            player_color = random.choice(["w", "b"])

        start_chess_battle(player_color=player_color)
    

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            
            # Route events to the correct buttons based on state
            if self.state == "MAIN_MENU":
                for btn in self.main_buttons: btn.handle_event(event)
            elif self.state == "OPTIONS":
                for btn in self.opt_buttons: btn.handle_event(event)
            elif self.state == "DIFFICULTY_SELECT":

                self.btn_diff_back.handle_event(event)

                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                    pos = event.pos
                    if self.easy_rect.collidepoint(pos):
                        self.start_difficulty("easy")
                    elif self.moderate_rect.collidepoint(pos):
                        self.start_difficulty("moderate")
                    elif self.hard_rect.collidepoint(pos):
                        self.start_difficulty("hard")

    def update(self):
        # Update animations
        if self.state == "MAIN_MENU":
            for orbiter in self.orbiters:
                orbiter.update()

    def draw(self):
        self.window.fill((20, 20, 25)) # Deep space background

        if self.state == "MAIN_MENU":
            self.draw_main_menu()
        elif self.state == "OPTIONS":
            self.draw_options()
        elif self.state == "DIFFICULTY_SELECT":
            self.draw_difficulty_select()

        pygame.display.flip()

    def draw_difficulty_select(self):
        
        mouse_pos = pygame.mouse.get_pos()
        title = self.font_title.render("Choose Difficulty",True,GOLD)

        self.window.blit(title,title.get_rect(center=(WIDTH//2, 100)))

        cards = [
            (self.easy_icon,"Easy","Always White",100),
            (self.moderate_icon,"Moderate","Random",400),
            (self.hard_icon,"Hard","Always Black",700)
        ]

        for icon, title_text, desc, x in cards:

            rect = pygame.Rect(x, 180, 220, 320)

            hovered = rect.collidepoint(mouse_pos)
            border_color = GOLD if hovered else WHITE
            pygame.draw.rect(self.window,DARK_GRAY,rect,border_radius=10)
            pygame.draw.rect(self.window,border_color,rect,3,border_radius=10)

            if icon:
                self.window.blit(icon, (x + 70, 220))

            title_surf = self.font_button.render(title_text,True,WHITE)

            self.window.blit(title_surf,title_surf.get_rect(center=(x + 110, 330)))

            desc_surf = self.font_text.render(desc,True,GRAY)

            self.window.blit(desc_surf,desc_surf.get_rect(center=(x + 110, 390)))

        self.btn_diff_back.draw(self.window)

    def draw_main_menu(self):
        # Draw Title
        title_surf = self.font_title.render("CHESS: OUTER GODS", True, GOLD)
        self.window.blit(title_surf, (WIDTH * 0.05, 100))

        # Draw Buttons (Left side)
        for btn in self.main_buttons:
            btn.draw(self.window)

        # Draw Black Hole (Right side)
        bh_center_x, bh_center_y = WIDTH * 0.75, HEIGHT // 2
        
        # Black hole aura
        for radius in range(120, 40, -10):
            alpha = int(255 * (radius / 120))
            color = (PURPLE[0], PURPLE[1], PURPLE[2], alpha)
            pygame.draw.circle(self.window, color, (bh_center_x, bh_center_y), radius)
        
        # Black hole core
        pygame.draw.circle(self.window, BLACK, (bh_center_x, bh_center_y), 50)
        pygame.draw.circle(self.window, WHITE, (bh_center_x, bh_center_y), 50, width=1)

        # Draw orbiting pieces
        for orbiter in self.orbiters:
            orbiter.draw(self.window, bh_center_x, bh_center_y)

    def draw_options(self):
        title = self.font_title.render("Options", True, WHITE)
        self.window.blit(title, title.get_rect(center=(WIDTH//2, 100)))
        
        # Subtext explaining difficulty
        desc = "(White = Easy, Any = Moderate, Black = Hard)"
        desc_surf = self.font_text.render(desc, True, GRAY)
        self.window.blit(desc_surf, desc_surf.get_rect(center=(WIDTH//2, 420)))

        for btn in self.opt_buttons:
            btn.draw(self.window)


if __name__ == "__main__":
    app = GameApp()
    app.run()