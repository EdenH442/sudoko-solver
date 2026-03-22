# from __future__ import annotations

# import argparse
# import csv
# import os
# import time
# from typing import Iterable

# from solvers.naive_solver import NaiveSolver


# def parse_board(puzzle: str) -> list[list[int]]:
#     puzzle = puzzle.strip()
#     if len(puzzle) < 81:
#         raise ValueError("Puzzle string must have at least 81 characters.")

#     board = [[0] * 9 for _ in range(9)]
#     for i, ch in enumerate(puzzle[:81]):
#         row = i // 9
#         col = i % 9
#         if ch in (".", "0"):
#             board[row][col] = 0
#         elif ch.isdigit():
#             board[row][col] = int(ch)
#         else:
#             raise ValueError(f"Invalid puzzle character: {ch!r}")
#     return board


# def iter_puzzles(csv_path: str) -> Iterable[tuple[int, str]]:
#     with open(csv_path, "r", encoding="utf-8", newline="") as f:
#         reader = csv.reader(f)
#         first_row = next(reader, None)
#         if first_row is None:
#             return

#         has_header = bool(first_row and first_row[0].strip().lower() == "question")
#         if has_header:
#             for idx, row in enumerate(reader, start=1):
#                 if not row:
#                     continue
#                 yield idx, row[0].strip()
#         else:
#             if first_row:
#                 yield 1, first_row[0].strip()
#             for idx, row in enumerate(reader, start=2):
#                 if not row:
#                     continue
#                 yield idx, row[0].strip()


# def solve_one(puzzle: str) -> tuple[bool, int, float]:
#     board = parse_board(puzzle)
#     solver = NaiveSolver(board)
#     steps = 0
#     solved = False
#     start = time.perf_counter()

#     for *_, status, solved_if_done in solver.solve_with_steps():
#         steps += 1
#         if status == "done":
#             solved = bool(solved_if_done)
#             break

#     elapsed = time.perf_counter() - start
#     return solved, steps, elapsed


# def main() -> None:
#     parser = argparse.ArgumentParser(
#         description=(
#             "Run NaiveSolver on puzzles from a CSV file and save per-puzzle "
#             "steps/time results."
#         )
#     )
#     parser.add_argument(
#         "--input",
#         default=os.path.join("data", "sudoku.csv"),
#         help="Input CSV path (default: data/sudoku.csv).",
#     )
#     parser.add_argument(
#         "--output",
#         default=os.path.join("results", "naive_solver_results.csv"),
#         help="Output CSV path (default: results/naive_solver_results.csv).",
#     )
#     parser.add_argument(
#         "--limit",
#         type=int,
#         default=None,
#         help="Optional number of puzzles to process from the top of the file.",
#     )
#     args = parser.parse_args()

#     os.makedirs(os.path.dirname(args.output), exist_ok=True)

#     processed = 0
#     with open(args.output, "w", encoding="utf-8", newline="") as out_f:
#         writer = csv.writer(out_f)
#         writer.writerow(["row_number", "solved", "steps", "solve_time_seconds"])

#         for row_number, puzzle in iter_puzzles(args.input):
#             if args.limit is not None and processed >= args.limit:
#                 break
#             solved, steps, elapsed = solve_one(puzzle)
#             writer.writerow([row_number, solved, steps, f"{elapsed:.6f}"])
#             processed += 1

#     print(f"Processed {processed} puzzles.")
#     print(f"Results saved to: {args.output}")


# if __name__ == "__main__":
#     main()
