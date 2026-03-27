from __future__ import annotations

import argparse
import csv
import os
from typing import Iterable

from solvers.base_solver import Board
from solvers.naive_solver import NaiveSolver
from solvers.csp_solver import CspSolver

# Later add more solvers here:
# from solvers.mrv_solver import MrvSolver

SOLVERS = {
    "naive": NaiveSolver,
    "csp": CspSolver,
}


def parse_board(puzzle: str) -> Board:
    puzzle = puzzle.strip()
    if len(puzzle) < 81:
        raise ValueError("Puzzle string must have at least 81 characters.")

    board = [[0] * 9 for _ in range(9)]
    for i, ch in enumerate(puzzle[:81]):
        row = i // 9
        col = i % 9

        if ch in (".", "0"):
            board[row][col] = 0
        elif ch.isdigit():
            board[row][col] = int(ch)
        else:
            raise ValueError(f"Invalid puzzle character: {ch!r}")

    return board


def iter_puzzles(csv_path: str) -> Iterable[tuple[int, str]]:
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        first_row = next(reader, None)
        if first_row is None:
            return

        has_header = bool(first_row and first_row[0].strip().lower() == "question")

        if has_header:
            for idx, row in enumerate(reader, start=1):
                if not row:
                    continue
                yield idx, row[0].strip()
        else:
            if first_row:
                yield 1, first_row[0].strip()

            for idx, row in enumerate(reader, start=2):
                if not row:
                    continue
                yield idx, row[0].strip()


def solve_one(puzzle: str, solver_name: str) -> dict[str, object]:
    solver_class = SOLVERS[solver_name]

    board = parse_board(puzzle)
    solver = solver_class(board)

    solved, elapsed = solver.run_with_time_analysis()

    return {
        "solver": solver.solver_name,
        "solved": solved,
        "solve_time_seconds": elapsed,
        "nodes_visited": solver.nodes_visited,
        "assignments": solver.assignments,
        "backtracks": solver.backtracks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run a Sudoku solver on puzzles from a CSV file and save per-puzzle "
            "benchmark results."
        )
    )
    parser.add_argument(
        "--input",
        default=os.path.join("data", "sudoku.csv"),
        help="Input CSV path (default: data/sudoku.csv).",
    )
    parser.add_argument(
        "--output",
        default=os.path.join("results", "solver_results.csv"),
        help="Output CSV path (default: results/solver_results.csv).",
    )
    parser.add_argument(
        "--solver",
        choices=sorted(SOLVERS.keys()),
        default="naive",
        help="Which solver to run.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of puzzles to process from the top of the file.",
    )
    args = parser.parse_args()

    print("=== Benchmark Configuration ===")
    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")
    print(f"Solver: {args.solver}")
    print(f"Limit: {args.limit}")
    print("================================")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    processed = 0
    with open(args.output, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(
            [
                "row_number",
                "solver",
                "solved",
                "solve_time_seconds",
                "nodes_visited",
                "assignments",
                "backtracks",
            ]
        )

        for row_number, puzzle in iter_puzzles(args.input):
            if args.limit is not None and processed >= args.limit:
                break

            print(f"Processing puzzle {processed + 1} (row {row_number})...")

            result = solve_one(puzzle, args.solver)
            
            writer.writerow(
                [
                    row_number,
                    result["solver"],
                    result["solved"],
                    f"{result['solve_time_seconds']:.6f}",
                    result["nodes_visited"],
                    result["assignments"],
                    result["backtracks"],
                ]
            )
            processed += 1

    print(f"Processed {processed} puzzles.")
    print(f"Solver: {args.solver}")
    print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
    