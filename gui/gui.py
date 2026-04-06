import pygame
import tkinter as tk
from tkinter import filedialog
import sys
import os
import random
import csv
import time
from solvers.naive_solver import NaiveSolver
from solvers.csp_mrv_solver import CspMrvSolver
from solvers.csp_forward_solver import CspForwardCheckingSolver
from solvers.csp_lcv_solver import CspLCVSolver

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
HIGHLIGHT_COLOR = (173, 216, 230)
SOLVING_COLOR = (100, 149, 237)
BACKGROUND_COLOR = (30, 30, 30)
BUTTON_COLOR = (50, 150, 200)
BUTTON_BORDER = (30, 30, 30)
FIXED_TEXT_COLOR = (255, 255, 255)

BUTTON_LABELS = [
    "Clean Board",
    "Load New Puzzle",
    "Solve (Naive)",
    "Solve (CSP)"
]
SOLVE_STEP_DELAY_MS = 120

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


def parse_puzzle_line(line: str):
    """Parse a single CSV/text line into a 9x9 board (list of lists).

    The input may be:
    * a contiguous 81-character string of digits/dots
    * comma/space separated numbers (81 tokens)
    * a CSV row containing extra columns (e.g. source, question, answer, rating)
      In that case we scan each field and pick the first one that looks like a
      puzzle (contains at least 81 digits/dots).

    Returns a 9x9 list of ints (0 for blank) or ``None`` if the line couldn't be
    interpreted.
    """
    s = line.strip()
    if not s:
        return None

    # helper that attempts to convert a single string fragment into a board
    def try_fragment(fragment: str):
        # comma/space separated tokens
        if "," in fragment or " " in fragment:
            parts = [p for p in fragment.replace(",", " ").split() if p]
            if len(parts) >= GRID_SIZE * GRID_SIZE:
                parts = parts[: GRID_SIZE * GRID_SIZE]
            elif len(parts) == GRID_SIZE:
                return None
            if len(parts) == GRID_SIZE * GRID_SIZE:
                board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
                for i, token in enumerate(parts):
                    r = i // GRID_SIZE
                    c = i % GRID_SIZE
                    if token in (".", "0"):
                        board[r][c] = 0
                    else:
                        try:
                            board[r][c] = int(token)
                        except ValueError:
                            board[r][c] = 0
                return board
        # contiguous format, remove everything except digits and dots
        compact = "".join(ch for ch in fragment if ch.isdigit() or ch == ".")
        if len(compact) >= GRID_SIZE * GRID_SIZE:
            compact = compact[: GRID_SIZE * GRID_SIZE]
            board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
            for i, ch in enumerate(compact):
                r = i // GRID_SIZE
                c = i % GRID_SIZE
                if ch == "." or ch == "0":
                    board[r][c] = 0
                else:
                    board[r][c] = int(ch)
            return board
        return None

    # if the line looks like a CSV row, split it and examine each field
    if "," in s:
        try:
            parts = next(csv.reader([s]))
        except Exception:
            parts = s.split(",")
        for part in parts:
            board = try_fragment(part)
            if board is not None:
                return board
        # none of the fields produced a board; fall through to try the whole line
    # finally try the entire string as one fragment
    return try_fragment(s)


def pick_random_puzzle_from_csv(path: str, exclude_line: str | None = None, tries: int = 5):
    """Select a random non-empty line from a CSV/text file and parse it into a board.

    Uses reservoir sampling to avoid loading the whole file. If the chosen line equals
    `exclude_line`, it will retry up to `tries` times.
    Returns (board, chosen_line) or (None, None) on failure.
    """
    if not os.path.exists(path):
        return None, None

    for attempt in range(tries):
        chosen = None
        chosen_line = None
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                count += 1
                if random.randrange(count) == 0:
                    chosen_line = line
        if chosen_line is None:
            return None, None
        if exclude_line and chosen_line == exclude_line:
            # try again
            continue
        board = parse_puzzle_line(chosen_line)
        if board is not None:
            return board, chosen_line
    return None, None


def resolve_default_puzzle_csv():
    """Return default puzzle CSV path, preferring sudoku.csv (0 = empty)."""
    data_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
    preferred = os.path.join(data_dir, "sudoku.csv")
    if os.path.exists(preferred):
        return preferred
    return os.path.join(data_dir, "validated_test.csv")


# --------------------------------------------------
# GUI class
# --------------------------------------------------

class SudokuGUI:
    def __init__(self, width=800, height=750):
        pygame.init()
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Sudoku Solver")
        self.clock = pygame.time.Clock()
        self._last_solved = None

        # compute geometry - fixed cell size to keep grid consistent
        self.cell_size = 60
        self.grid_offset = (
            (self.window_width - self.cell_size * GRID_SIZE) // 2,
            85,
        )

        # state
        self.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        # `fixed` marks cells that came from a loaded puzzle and cannot be changed
        self.fixed = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.selected_cell = None
        self.solving_cell = None
        self.font = pygame.font.SysFont("arial", self.cell_size // 2)
        self.button_font = pygame.font.SysFont("arial", 20)
        self.stats_font = pygame.font.SysFont("arial", 22)
        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.running = True
        self._last_loaded_line = None
        self._solve_steps = None
        self._last_solve_step_ms = 0
        self._solve_step_count = 0
        self._solve_start_time = 0.0
        self._last_result_steps = None
        self._last_result_time = None
        self._active_solver_name = None

        # Try to load an initial puzzle from validated_test.csv
        test_path = resolve_default_puzzle_csv()
        if os.path.exists(test_path):
            try:
                self.load_random_test_puzzle(test_path)
            except Exception:
                # ignore and continue with empty board
                logger.exception("Failed to auto-load initial puzzle from %s", test_path)

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

    def draw_title(self):
        title_text = "SUDOKU SOLVER"
        txt = self.title_font.render(title_text, True, WHITE)
        txtrect = txt.get_rect(center=(self.window_width // 2, 40))
        self.screen.blit(txt, txtrect)

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
                    # render fixed (loaded) values slightly differently and non-editable
                    color = FIXED_TEXT_COLOR if self.fixed[r][c] else BLACK
                    txt = self.font.render(str(value), True, color)
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
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, BUTTON_BORDER, rect, 2, border_radius=10)
            txt = self.button_font.render(label, True, TEXT_COLOR)
            txtrect = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txtrect)

    def draw_solver_results(self):
        rects = self._button_rects()
        if not rects:
            return
        base_y = rects[0].bottom + 22
        steps_value = "" if self._last_result_steps is None else str(self._last_result_steps)
        time_value = "" if self._last_result_time is None else f"{self._last_result_time:.2f}s"

        result_text = self.stats_font.render(
        f"Steps: {steps_value}   |   Time: {time_value}",
        True,
        WHITE,
        )
        result_rect = result_text.get_rect(center=(self.window_width // 2, base_y))
        self.screen.blit(result_text, result_rect)

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
                # mark non-zero cells as fixed (immutable)
                self.fixed = [[self.board[r][c] != 0 for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
                self.selected_cell = None
            except Exception as e:
                logger.exception("Failed to load puzzle: %s", e)

    def load_random_test_puzzle(self, path: str | None = None):
        """Load a random puzzle from the configured CSV (default: sudoku.csv).

        Avoids re-loading the same puzzle twice in a row when possible.
        """
        if path is None:
            path = resolve_default_puzzle_csv()
        if not os.path.exists(path):
            logger.error("Required puzzle CSV not found: %s", path)
            return
        board, chosen_line = pick_random_puzzle_from_csv(path, exclude_line=self._last_loaded_line)
        if board is None:
            logger.error("No valid puzzle rows found in: %s", path)
            return
        self.board = board
        # mark loaded cells as fixed
        self.fixed = [[self.board[r][c] != 0 for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.selected_cell = None
        self._last_loaded_line = chosen_line

    # ---------- main loop ----------
    def run(self):
        while self.running:
            self.screen.fill(BACKGROUND_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._solve_steps is not None:
                        continue
                    cell = self.handle_grid_click(event.pos)
                    if cell:
                        self.selected_cell = cell
                    else:
                        action = self.handle_button_click(event.pos)
                        if action:
                            self._perform_action(action)
                elif event.type == pygame.KEYDOWN and self.selected_cell:
                    if self._solve_steps is not None:
                        continue
                    c, r = self.selected_cell
                    # Do not allow editing fixed (loaded) cells
                    if self.fixed[r][c]:
                        continue
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        self.board[r][c] = 0
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        self.board[r][c] = event.key - pygame.K_0

            if self._solve_steps is not None:
                now_ms = pygame.time.get_ticks()
                if now_ms - self._last_solve_step_ms >= SOLVE_STEP_DELAY_MS:
                    self._last_solve_step_ms = now_ms
                    try:
                        board, active_cell, status, solved_if_done = next(self._solve_steps)
                        self._solve_step_count += 1
                        self.board = board
                        self.solving_cell = active_cell

                        if status == "done":
                            self._last_solved = solved_if_done
                            self._finalize_solve_stats()
                    except StopIteration:
                        self._finalize_solve_stats()

            self.draw_title()
            self.draw_grid()
            self.draw_board()
            self.draw_buttons()
            self.draw_solver_results()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def _perform_action(self, action_name):
        if action_name == "load_new_puzzle":
            # load from configured default CSV (prefers sudoku.csv)
            test_path = resolve_default_puzzle_csv()
            if os.path.exists(test_path):
                self.load_random_test_puzzle(test_path)
            else:
                logger.error("Required puzzle CSV not found: %s", test_path)
        elif action_name == "clean_board":
            # clear only non-fixed cells
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if not self.fixed[r][c]:
                        self.board[r][c] = 0
            self.selected_cell = None
        elif action_name == "solve_(naive)":
             self._start_solver_animation(NaiveSolver(self.board), "Naive")
        elif action_name == "solve_(csp)":
            self._start_solver_animation(CspLCVSolver(self.board), "MRV+CSP")
        else:
            # no additional buttons available; log unexpected
            logger.warning("Unhandled button action: %s", action_name)

    def _start_solver_animation(self, solver, solver_name: str):
        self._active_solver_name = solver_name
        self._solve_steps = solver.solve_with_steps()
        self._last_solve_step_ms = pygame.time.get_ticks()
        self._solve_step_count = 0
        self._solve_start_time = time.perf_counter()
        self._last_result_steps = None
        self._last_result_time = None
        self._last_solved = None
        self.selected_cell = None
        self.solving_cell = None
    
    def _finalize_solve_stats(self):
        if self._solve_steps is None:
            return
        elapsed = time.perf_counter() - self._solve_start_time
        solved = bool(self._last_solved)
        status = "Solved" if solved else "No solution found"
        self._last_result_steps = self._solve_step_count
        self._last_result_time = elapsed
        solver_name = self._active_solver_name or "Solver"
        print(f"{solver_name} Solver finished: {status}")
        print(f"Steps: {self._solve_step_count}")
        print(f"Time: {elapsed:.2f} seconds")
        logger.info(
            "%s Solver finished | status=%s | steps=%d | time=%.2fs",
            solver_name,
            status,
            self._solve_step_count,
            elapsed,
        )
        self._solve_steps = None
        self.solving_cell = None
        self._active_solver_name = None


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    gui = SudokuGUI()
    gui.run()
