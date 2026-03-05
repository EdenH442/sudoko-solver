from __future__ import annotations

from typing import Generator, Optional, Tuple

from .base_solver import BaseSolver, Step


class NaiveSolver(BaseSolver):
    def run(self) -> bool:
        if not self._is_board_consistent():
            return False
        return self._solve_recursive()

    def solve_with_steps(self) -> Generator[Step, None, None]:
        if not self._is_board_consistent():
            yield self.board, None, "done", False
            return
        solved = yield from self._solve_with_steps_recursive()
        yield self.board, None, "done", solved

    def _solve_recursive(self) -> bool:
        pos = self._find_next_empty_pos()
        if pos is None:
            return True

        row, col = pos
        for value in range(1, 10):
            if not self._is_valid(row, col, value):
                continue
            self.board[row][col] = value
            if self._solve_recursive():
                return True
            self.board[row][col] = 0

        return False

    def _solve_with_steps_recursive(self) -> Generator[Step, None, bool]:
        pos = self._find_next_empty_pos()
        if pos is None:
            return True

        row, col = pos
        for value in range(1, 10):
            if not self._is_valid(row, col, value):
                continue
            self.board[row][col] = value
            yield self.board, (col, row), "progress", None

            solved = yield from self._solve_with_steps_recursive()
            if solved:
                return True

            self.board[row][col] = 0
            yield self.board, (col, row), "progress", None

        return False

    def _find_next_empty_pos(self) -> Optional[Tuple[int, int]]:
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return row, col
        return None

    def _is_board_consistent(self) -> bool:
        for row in range(9):
            for col in range(9):
                value = self.board[row][col]
                if value == 0:
                    continue
                if not self._is_valid(row, col, value):
                    return False
        return True

    def _is_valid(self, row: int, col: int, value: int) -> bool:
        for c in range(9):
            if c != col and self.board[row][c] == value:
                return False
        for r in range(9):
            if r != row and self.board[r][col] == value:
                return False

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col) and self.board[r][c] == value:
                    return False
        return True
