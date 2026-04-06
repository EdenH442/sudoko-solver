from __future__ import annotations
from typing import Generator

from .base_solver import BaseSolver, Step
from sudoku.board_utils import is_board_consistent, is_valid

class CspMrvSolver(BaseSolver):
    solver_name = "csp_mrv"

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
        
        selection = self.select_unassigned_variable() # select next variable using MRV Function
        if selection is None:
            return True # puzzle should be solved
        
        row, col, domain = selection
        if(len(domain) == 0):
            return False # cell empty but no legal values - impossible cell, backtrack
        
        ordered_domain = self.order_domain_values(row, col, domain)

        for value in ordered_domain:
            self.board[row][col] = value
            self.assignments += 1

            if self._solve_recursive():
                return True
            
            self.board[row][col] = 0
            self.backtracks += 1
        return False

    def _solve_with_steps_recursive(self) -> Generator[Step, None, bool]:
        self.nodes_visited += 1

        selection = self.select_unassigned_variable() # select next variable using MRV Function
        if selection is None:
            return True # puzzle should be solved

        row, col, domain = selection
        if(len(domain) == 0):
            return False # cell empty but no legal values - impossible cell, backtrack
        
        ordered_domain = self.order_domain_values(row, col, domain)

        for value in ordered_domain:
            self.board[row][col] = value
            self.assignments +=1
            yield self.board, (col, row), "progress", None # yeilding for visualization after assignment

            solved = yield from self._solve_with_steps_recursive()
            if solved:
                return True
            
            self.board[row][col] = 0
            self.backtracks += 1
            yield self.board, (col, row), "progress", None
        
        return False

    # Variables for this problem is the empty cells.
    # Domains for each variable is the possible values (from 1 to 9) that can be assigned to that cell 
    # without violating the Sudoku rules.

    def get_domain(self, row: int, col: int) -> list[int]:
        if(self.board[row][col] != 0):
            return [] # no domain for already filled cells, they are not variables in the CSP sense
        
        domain: list[int] = []

        for value in range(1, 10):
            if is_valid(self.board, row, col, value):
                domain.append(value)
            
        return domain

    #choose next cell using Minimum Remaining Values (MRV) heuristic, 
    # which selects the variable with the fewest legal values in its domain.
    def select_unassigned_variable(self) -> tuple[int, int, list[int]] | None:
        best_row = -1
        best_col = -1
        best_domain: list[int] | None = None

        for row in range(9):
            for col in range(9):
                if(self.board[row][col] != 0):
                    continue # skip already filled cells

                domain = self.get_domain(row, col)
                if(len(domain) == 0):
                    return row,col, domain  #cell empty but no legal values - impossible cell.
                
                if best_domain is None or len(domain) < len(best_domain):
                    best_row = row
                    best_col = col
                    best_domain = domain
                
        if best_domain is None:
            return None # no unassigned variables left, should be solved
            
        return best_row, best_col, best_domain
    
    def order_domain_values(self, row: int, col: int, domain: list[int]) -> list[int]:
        return domain
                
