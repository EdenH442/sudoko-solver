from __future__ import annotations

from abc import ABC, abstractmethod
import time
from typing import Generator, Literal, Optional, Tuple

Board = list[list[int]]
Cell = Optional[Tuple[int, int]]
Status = Literal["progress", "done"]
Step = tuple[Board, Cell, Status, Optional[bool]]


class BaseSolver(ABC):
    def __init__(self, board: Board):
        self.board = board

    @abstractmethod
    def run(self) -> bool:
        """Solve the board in place and return True if solved."""
        raise NotImplementedError("run not implemented")

    @abstractmethod
    def solve_with_steps(self) -> Generator[Step, None, None]:
        """Yield (board, active_cell, status, solved_if_done)."""
        raise NotImplementedError("solve_with_steps not implemented")

    def run_with_time_analysis(self) -> tuple[bool, float]:
        start_time = time.perf_counter()
        solved = self.run()
        return solved, (time.perf_counter() - start_time)
