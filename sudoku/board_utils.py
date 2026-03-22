from __future__ import annotations

from typing import Optional, Tuple

Board = list[list[int]]
Position = Optional[Tuple[int, int]]


def find_next_empty_pos(board: Board) -> Position:
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col
    return None


def is_valid(board: Board, row: int, col: int, value: int) -> bool:
    # Check row
    for c in range(9):
        if c != col and board[row][c] == value:
            return False

    # Check column
    for r in range(9):
        if r != row and board[r][col] == value:
            return False

    # Check 3x3 box
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if (r, c) != (row, col) and board[r][c] == value:
                return False

    return True


def is_board_consistent(board: Board) -> bool:
    for row in range(9):
        for col in range(9):
            value = board[row][col]
            if value == 0:
                continue
            if not is_valid(board, row, col, value):
                return False
    return True


def get_candidates(board: Board, row: int, col: int) -> set[int]:
    if board[row][col] != 0:
        return set()

    candidates: set[int] = set()
    for value in range(1, 10):
        if is_valid(board, row, col, value):
            candidates.add(value)
    return candidates