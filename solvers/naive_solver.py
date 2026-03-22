from __future__ import annotations

from typing import Generator

from .base_solver import BaseSolver, Step
from sudoku.board_utils import find_next_empty_pos, is_board_consistent, is_valid


class NaiveSolver(BaseSolver):
    solver_name = "naive"

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

    def _solve_recursive(self) -> bool:
        self.nodes_visited += 1

        pos = find_next_empty_pos(self.board)
        if pos is None:
            return True

        row, col = pos
        for value in range(1, 10):
            if not is_valid(self.board, row, col, value):
                continue

            self.board[row][col] = value
            self.assignments += 1

            if self._solve_recursive():
                return True

            self.board[row][col] = 0
            self.backtracks += 1

        return False

    def _solve_with_steps_recursive(self) -> Generator[Step, None, bool]:
        self.nodes_visited += 1

        pos = find_next_empty_pos(self.board)
        if pos is None:
            return True

        row, col = pos
        for value in range(1, 10):
            if not is_valid(self.board, row, col, value):
                continue

            self.board[row][col] = value
            self.assignments += 1
            yield self.board, (col, row), "progress", None

            solved = yield from self._solve_with_steps_recursive()
            if solved:
                return True

            self.board[row][col] = 0
            self.backtracks += 1
            yield self.board, (col, row), "progress", None

        return False
    