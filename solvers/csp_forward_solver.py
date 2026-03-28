from __future__ import annotations
from typing import Generator

from .base_solver import BaseSolver, Step
from sudoku.board_utils import is_board_consistent, is_valid

class CspForwardCheckingSolver(BaseSolver):
    solver_name = "csp_forward"

    def run(self) -> bool:
        if not is_board_consistent(self.board):
            return False
        return self._solve_recursive()
    
    def solve_with_steps(self) -> Generator[Step, None, None]:
        if not is_board_consistent(self.board):
            yield self.board, None, "done", False
            return

        self.reset_metrics()
        solved = yield from self._solve_with_steps_recursive()
        yield self.board, None, "done", solved

        
    def get_domain(self, row: int, col: int) -> list[int]:
        if self.board[row][col] != 0:
            return []

        domain: list[int] = []
        for value in range(1, 10):
            if is_valid(self.board, row, col, value):
                domain.append(value)

        return domain
    
    def _solve_recursive(self) -> bool:
        self.nodes_visited += 1

        selection = self.select_unassigned_variable()
        if selection is None:
            return True

        row, col, domain = selection
        if len(domain) == 0:
            return False

        for value in domain:
            self.board[row][col] = value
            self.assignments += 1

            if self.forward_check(row, col) and self._solve_recursive():
                return True

            self.board[row][col] = 0
            self.backtracks += 1

        return False
    
    def _solve_with_steps_recursive(self) -> Generator[Step, None, bool]:
        self.nodes_visited += 1

        selection = self.select_unassigned_variable()
        if selection is None:
            return True

        row, col, domain = selection
        if len(domain) == 0:
            return False

        for value in domain:
            self.board[row][col] = value
            self.assignments += 1
            yield self.board, (col, row), "progress", None

            if self.forward_check(row, col):
                solved = yield from self._solve_with_steps_recursive()
                if solved:
                    return True

            self.board[row][col] = 0
            self.backtracks += 1
            yield self.board, (col, row), "progress", None

        return False
    
    def select_unassigned_variable(self) -> tuple[int, int, list[int]] | None:
        best_row = -1
        best_col = -1
        best_domain: list[int] | None = None

        for row in range(9):
            for col in range(9):
                if self.board[row][col] != 0:
                    continue

                domain = self.get_domain(row, col)
                if len(domain) == 0:
                    return row, col, domain

                if best_domain is None or len(domain) < len(best_domain):
                    best_row = row
                    best_col = col
                    best_domain = domain

        if best_domain is None:
            return None

        return best_row, best_col, best_domain
    
    def forward_check(self, row:int, col: int) -> bool:
        # After assigning board[row][col], check all affected unassigned neighbors
        # If any neighbor has an empty domain, return False to trigger backtracking

        for neighbor_row, neighbor_col in self.get_neighboring_unassigned_cells(row, col):
            domain = self.get_domain(neighbor_row, neighbor_col)
            if len(domain) == 0:
                return False
        return True
    
    def get_neighboring_unassigned_cells(self, row: int, col: int) -> set[tuple[int, int]]:
        neighbors: set[tuple[int, int]] = set() #so no duplicates to check

        # Check Same row
        for c in range(9):
            if c != col and self.board[row][c] == 0:
                neighbors.add((row, c))

        # Check Same column
        for r in range(9):
            if r != row and self.board[r][col] == 0:
                neighbors.add((r, col))
        
        # Check Same 3x3 box
        start_row = (row // 3) * 3
        start_col = (col // 3) * 3
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if (r,c) != (row,col) and self.board[r][c] == 0:
                    neighbors.add((r,c))
        
        return neighbors