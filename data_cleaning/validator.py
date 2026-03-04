import csv
import os
from typing import List, Tuple


class SudokuValidator:
    """Validates whether a given Sudoku puzzle is valid."""
    
    @staticmethod
    def is_valid_puzzle(puzzle: str) -> bool:
        """
        Check if a puzzle string is a valid Sudoku puzzle.
        
        Args:
            puzzle: String representation of Sudoku (81 characters, digits 0-9 where 0 = empty)
        
        Returns:
            True if valid, False otherwise
        """
        # Check if it's a valid format
        if not isinstance(puzzle, str):
            return False
        
        if len(puzzle) != 81:
            return False
        
        # Check if all characters are digits
        if not puzzle.isdigit():
            return False
        
        # Check if puzzle only contains 0-9
        if not all(c in '0123456789' for c in puzzle):
            return False
        
        # Convert to 9x9 grid and validate
        grid = SudokuValidator._string_to_grid(puzzle)
        
        # Check rows, columns, and 3x3 boxes for duplicates
        return SudokuValidator._validate_structure(grid)
    
    @staticmethod
    def is_valid_solution(solution: str) -> bool:
        """
        Check if a solution string is a valid completed Sudoku puzzle.
        
        Args:
            solution: String representation of Sudoku (81 characters, digits 1-9 only, no empty cells)
        
        Returns:
            True if valid solution, False otherwise
        """
        # Check if it's a valid format
        if not isinstance(solution, str):
            return False
        
        if len(solution) != 81:
            return False
        
        # Check if all characters are digits
        if not solution.isdigit():
            return False
        
        # Check if solution only contains 1-9 (no 0s - must be complete)
        if not all(c in '123456789' for c in solution):
            return False
        
        # Convert to 9x9 grid and validate
        grid = SudokuValidator._string_to_grid(solution)
        
        # Check rows, columns, and 3x3 boxes for duplicates
        return SudokuValidator._validate_structure(grid)
    
    @staticmethod
    def _string_to_grid(puzzle: str) -> List[List[int]]:
        """Convert puzzle string to 9x9 grid."""
        grid = []
        for i in range(9):
            row = [int(puzzle[i * 9 + j]) for j in range(9)]
            grid.append(row)
        return grid
    
    @staticmethod
    def _validate_structure(grid: List[List[int]]) -> bool:
        """Check if grid has valid structure (no duplicate non-zero values in rows, cols, boxes)."""
        
        # Check rows
        for row in grid:
            non_zero = [x for x in row if x != 0]
            if len(non_zero) != len(set(non_zero)):
                return False
        
        # Check columns
        for col in range(9):
            column = [grid[row][col] for row in range(9)]
            non_zero = [x for x in column if x != 0]
            if len(non_zero) != len(set(non_zero)):
                return False
        
        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(grid[box_row * 3 + i][box_col * 3 + j])
                non_zero = [x for x in box if x != 0]
                if len(non_zero) != len(set(non_zero)):
                    return False
        
        return True


def clean_csv(
    input_file: str,
    output_file: str,
    puzzle_column: int = 0,
    validate_solution: bool = False,
    answer_column: int | None = None,
) -> Tuple[int, int, int]:
    """
    Process a CSV file and validate Sudoku puzzles or solutions.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file with validation results
        puzzle_column: Column index containing the puzzle string (default: 0)
        validate_solution: If True, validate solutions (completed puzzles with 1-9 only).
                          If False (default), validate puzzles (can have 0-9 where 0 = empty)
        answer_column: Optional column index containing a corresponding solution.  If
                       provided, that column will be checked using
                       ``is_valid_solution`` regardless of ``validate_solution``.
    
    Returns:
        Tuple of (total_rows, valid_puzzles, invalid_puzzles)
    """
    validator = SudokuValidator()
    valid_count = 0
    invalid_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Write header with validation status
        header = next(reader)
        header.append('is_valid')
        writer.writerow(header)
        
        for row_idx, row in enumerate(reader, start=1):
            # decide which field to validate
            if answer_column is not None and len(row) > answer_column:
                target = row[answer_column]
                check_solution = True
            elif len(row) > puzzle_column:
                target = row[puzzle_column]
                check_solution = validate_solution
            else:
                # missing expected column
                row.append('False')
                writer.writerow(row)
                invalid_count += 1
                continue

            # normalize: replace dots with zero for puzzles
            if not check_solution:
                target = target.replace('.', '0')

            if check_solution:
                is_valid = validator.is_valid_solution(target)
            else:
                is_valid = validator.is_valid_puzzle(target)

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            row.append(str(is_valid))
            writer.writerow(row)
    
    total = valid_count + invalid_count
    return total, valid_count, invalid_count


def filter_csv_inplace(
    file_path: str,
    puzzle_column: int = 0,
    validate_solution: bool = False,
    answer_column: int | None = None,
) -> Tuple[int, int]:
    """
    Remove invalid rows from a CSV file in place.

    Reads the entire file, validates each row, and rewrites the file containing
    only the header and valid rows. The header is assumed to be the first line
    of the file and is always preserved. A tuple of (kept_rows, removed_rows)
    is returned, and a summary message is printed.
    """
    kept_rows = []
    removed = 0

    # read and validate
    with open(file_path, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        try:
            header = next(reader)
        except StopIteration:
            # empty file
            print(f"File '{file_path}' is empty, nothing to filter.")
            return 0, 0
        kept_rows.append(header)

        for row in reader:
            if answer_column is not None and len(row) > answer_column:
                target = row[answer_column]
                check_solution = True
            elif len(row) > puzzle_column:
                target = row[puzzle_column]
                check_solution = validate_solution
            else:
                # no puzzle column, drop row
                removed += 1
                continue

            if not check_solution:
                target = target.replace('.', '0')
            if check_solution:
                valid = SudokuValidator.is_valid_solution(target)
            else:
                valid = SudokuValidator.is_valid_puzzle(target)

            if valid:
                kept_rows.append(row)
            else:
                removed += 1

    # overwrite file using temp
    tmp = file_path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(kept_rows)
    os.replace(tmp, file_path)

    kept = len(kept_rows) - 1
    print(f"Filtered '{file_path}': kept {kept} rows, removed {removed} invalid rows")
    return kept, removed


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validator.py <input_csv> [output_csv] [puzzle_column]")
        print("Example: python validator.py ../data/test.csv cleaned_test.csv 0")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "cleaned_" + input_csv
    puzzle_col = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    
    print(f"Processing {input_csv}...")
    total, valid, invalid = clean_csv(input_csv, output_csv, puzzle_col)
    
    print(f"\nResults:")
    print(f"  Total rows: {total}")
    print(f"  Valid puzzles: {valid}")
    print(f"  Invalid puzzles: {invalid}")
    print(f"  Output saved to: {output_csv}")
