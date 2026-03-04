from __future__ import annotations

from abc import ABC, abstractmethod
import time
from typing import Generator, Optional, Tuple

Board = list[list[int]]
Step = tuple[Board, Optional[Tuple[int, int]]]


class BaseSolver(ABC):
    def __init__(self, board: Board):
        self.board = board

    @abstractmethod
    def run(self) -> bool:
        """Solve the board in place and return True if solved."""
        raise NotImplementedError("run not implemented")

    @abstractmethod
    def solve_with_steps(self) -> Generator[Step, None, None]:
        """Yield (board, active_cell) as the solver progresses."""
        raise NotImplementedError("solve_with_steps not implemented")

    def run_with_time_analysis(self) -> tuple[bool, float]:
        start_time = time.perf_counter()
        solved = self.run()
        return solved, (time.perf_counter() - start_time)
