from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Generator, Literal, Optional, Tuple

Board = list[list[int]]
Cell = Optional[Tuple[int, int]]
Status = Literal["progress", "done"]
Step = tuple[Board, Cell, Status, Optional[bool]]


class BaseSolver(ABC):
    solver_name: str = "base"

    def __init__(self, board: Board):
        self.board = board

        # Metrics for benchmark comparison
        self.nodes_visited = 0
        self.assignments = 0
        self.backtracks = 0

    @abstractmethod
    def run(self) -> bool:
        """Solve the board in place and return True if solved."""
        raise NotImplementedError("run not implemented")

    @abstractmethod
    def solve_with_steps(self) -> Generator[Step, None, None]:
        """Yield (board, active_cell, status, solved_if_done) for visualization."""
        raise NotImplementedError("solve_with_steps not implemented")

    def reset_metrics(self) -> None:
        self.nodes_visited = 0
        self.assignments = 0
        self.backtracks = 0

    def run_with_time_analysis(self) -> tuple[bool, float]:
        self.reset_metrics()
        start_time = time.perf_counter()
        solved = self.run()
        elapsed = time.perf_counter() - start_time
        return solved, elapsed
    