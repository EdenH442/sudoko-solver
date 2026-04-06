from __future__ import annotations

from .csp_mrv_solver import CspMrvSolver

class CspLCVSolver(CspMrvSolver):
    solver_name = "csp_lcv"

    def order_domain_values(self, row: int, col: int, domain: list[int]) -> list[int]:
        return sorted(domain, key=lambda value: self.count_constraints(row, col, value))
    
    def count_constraints(self, row: int, col: int, value: int) -> int:
        score = 0

        for neighbor_row, neighbor_col in self.get_unassigned_neighbors(row, col):
            neighbor_domain = self.get_domain(neighbor_row, neighbor_col)
            if value in neighbor_domain:
                score += 1

        return score
    
    def get_unassigned_neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        neighbors: set[tuple[int, int]] = set()

        for c in range(9):
            if c != col and self.board[row][c] == 0:
                neighbors.add((row, c))

        for r in range(9):
            if r != row and self.board[r][col] == 0:
                neighbors.add((r, col))

        box_row_start = (row // 3) * 3
        box_col_start = (col // 3) * 3

        for r in range(box_row_start, box_row_start + 3):
            for c in range(box_col_start, box_col_start + 3):
                if (r, c) != (row, col) and self.board[r][c] == 0:
                    neighbors.add((r, c))

        return list(neighbors)