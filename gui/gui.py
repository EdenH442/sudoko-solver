import pygame
import tkinter as tk
from tkinter import filedialog
import sys

# Configure logger if you have one in the main application
import logging
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Constants & colors
# --------------------------------------------------
GRID_SIZE = 9
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (200, 200, 200)
HOVER_COLOR = (170, 170, 170)
TEXT_COLOR = (50, 50, 50)
HIGHLIGHT_COLOR = (240, 128, 128)
SOLVING_COLOR = (100, 149, 237)
BACKGROUND_COLOR = (30, 30, 30)
BUTTON_COLOR = (50, 150, 200)
BUTTON_BORDER = (30, 30, 30)

BUTTON_LABELS = [
    "Clean Board",
    "Load New Puzzle",
]

# --------------------------------------------------
# Utility functions
# --------------------------------------------------

def load_board_from_file(path: str):
    """Load a 9x9 board from a text file. Accepts commas or spaces.

    The file should contain exactly 9 lines with 9 numbers each.
    Empty cells may be represented by 0 or a dot.
    """
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    with open(path, "r", encoding="utf-8") as f:
        for r, line in enumerate(f):
            if r >= GRID_SIZE:
                break
            parts = [p for p in line.strip().replace(",", " ").split() if p]
            for c, token in enumerate(parts[:GRID_SIZE]):
                if token in (".", "0"):
                    board[r][c] = 0
                else:
                    try:
                        board[r][c] = int(token)
                    except ValueError:
                        board[r][c] = 0
    return board


# --------------------------------------------------
# GUI class
# --------------------------------------------------

class SudokuGUI:
    def __init__(self, width=800, height=700):
        pygame.init()
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Sudoku Solver")
        self.clock = pygame.time.Clock()

        # compute geometry
        self.cell_size = min(self.window_width, self.window_height - 120) // GRID_SIZE
        self.grid_offset = (
            (self.window_width - self.cell_size * GRID_SIZE) // 2,
            20,
        )

        # state
        self.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.selected_cell = None
        self.solving_cell = None
        self.font = pygame.font.SysFont("arial", self.cell_size // 2)
        self.button_font = pygame.font.SysFont("arial", 20)
        self.running = True

    # ---------- drawing helpers ----------
    def draw_grid(self):
        grid_size_px = self.cell_size * GRID_SIZE
        x_off, y_off = self.grid_offset
        for i in range(GRID_SIZE + 1):
            line_width = 3 if i % 3 == 0 else 1
            pygame.draw.line(
                self.screen,
                BLACK,
                (x_off, y_off + i * self.cell_size),
                (x_off + grid_size_px, y_off + i * self.cell_size),
                line_width,
            )
            pygame.draw.line(
                self.screen,
                BLACK,
                (x_off + i * self.cell_size, y_off),
                (x_off + i * self.cell_size, y_off + grid_size_px),
                line_width,
            )

    def draw_board(self):
        x_off, y_off = self.grid_offset
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                value = self.board[r][c]
                cell_rect = pygame.Rect(
                    x_off + c * self.cell_size,
                    y_off + r * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )

                if self.selected_cell == (c, r):
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, cell_rect)
                if self.solving_cell == (c, r):
                    pygame.draw.rect(self.screen, SOLVING_COLOR, cell_rect)

                if value != 0:
                    txt = self.font.render(str(value), True, BLACK)
                    txtrect = txt.get_rect(center=cell_rect.center)
                    self.screen.blit(txt, txtrect)

    def _button_rects(self):
        button_w = 140
        button_h = 40
        spacing = 15
        total_w = len(BUTTON_LABELS) * button_w + (len(BUTTON_LABELS) - 1) * spacing
        start_x = (self.window_width - total_w) // 2
        y = self.grid_offset[1] + self.cell_size * GRID_SIZE + 30
        rects = []
        for idx, _ in enumerate(BUTTON_LABELS):
            rects.append(
                pygame.Rect(start_x + idx * (button_w + spacing), y, button_w, button_h)
            )
        return rects

    def draw_buttons(self):
        rects = self._button_rects()
        mx, my = pygame.mouse.get_pos()
        for rect, label in zip(rects, BUTTON_LABELS):
            color = BUTTON_COLOR
            if rect.collidepoint((mx, my)):
                color = HOVER_COLOR
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BUTTON_BORDER, rect, 2)
            txt = self.button_font.render(label, True, TEXT_COLOR)
            txtrect = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txtrect)

    # ---------- input / event handling ----------
    def handle_button_click(self, pos):
        for rect, label in zip(self._button_rects(), BUTTON_LABELS):
            if rect.collidepoint(pos):
                action = label.lower().replace(" ", "_")
                return action
        return None

    def handle_grid_click(self, pos):
        x, y = pos
        x_off, y_off = self.grid_offset
        if x_off <= x < x_off + self.cell_size * GRID_SIZE and y_off <= y < y_off + self.cell_size * GRID_SIZE:
            row = (y - y_off) // self.cell_size
            col = (x - x_off) // self.cell_size
            return int(col), int(row)
        return None

    def load_puzzle(self):
        # use tkinter filedialog without showing window
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select puzzle file",
            filetypes=[("Text files", "*.txt;*.csv"), ("All files", "*")],
        )
        root.destroy()
        if file_path:
            try:
                self.board = load_board_from_file(file_path)
                self.selected_cell = None
            except Exception as e:
                logger.exception("Failed to load puzzle: %s", e)

    # ---------- main loop ----------
    def run(self):
        while self.running:
            self.screen.fill(BACKGROUND_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    cell = self.handle_grid_click(event.pos)
                    if cell:
                        self.selected_cell = cell
                    else:
                        action = self.handle_button_click(event.pos)
                        if action:
                            self._perform_action(action)
                elif event.type == pygame.KEYDOWN and self.selected_cell:
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        c, r = self.selected_cell
                        self.board[r][c] = 0
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        c, r = self.selected_cell
                        self.board[r][c] = event.key - pygame.K_0
            self.draw_grid()
            self.draw_board()
            self.draw_buttons()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def _perform_action(self, action_name):
        if action_name == "load_new_puzzle":
            self.load_puzzle()
        elif action_name == "clean_board":
            self.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
            self.selected_cell = None
        else:
            # no additional buttons available; log unexpected
            logger.warning("Unhandled button action: %s", action_name)


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    gui = SudokuGUI()
    gui.run()
