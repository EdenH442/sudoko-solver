"""
Main script to run validation on all Sudoku CSV files.
"""

import os
import sys
from pathlib import Path
from validator import clean_csv, filter_csv_inplace


def validate_all_csvs(
    data_dir: str = "../data",
    output_dir: str = None,
    validate_solution: bool = False,
    answer_column: int | None = None,
):
    """
    Validate all CSV files in the data directory.
    
    Args:
        data_dir: Directory containing CSV files to validate
        output_dir: Directory to save validated CSV files. If None, uses data_dir itself.
        validate_solution: If True, validate solutions (completed puzzles). If False, validate puzzles.
        answer_column: Optional column index in each file where a completed solution
                       resides. When provided the validator will check that column as a
                       full solution instead of the puzzle column.
    """
    
    # default output directory is data_dir when not specified
    if output_dir is None:
        output_dir = data_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all CSV files
    data_path = Path(data_dir)
    csv_files = list(data_path.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV file(s) to validate\n")
    print("=" * 60)
    
    total_stats = {"total": 0, "valid": 0, "invalid": 0}
    
    for csv_file in csv_files:
        print(f"\nProcessing: {csv_file.name}")
        print("-" * 60)
        
        output_file = os.path.join(output_dir, f"validated_{csv_file.name}")
        
        try:
            total, valid, invalid = clean_csv(
                str(csv_file),
                output_file,
                puzzle_column=0,
                validate_solution=validate_solution,
                answer_column=answer_column,
            )
            
            total_stats["total"] += total
            total_stats["valid"] += valid
            total_stats["invalid"] += invalid
            
            print(f"  Total rows: {total}")
            print(f"  Valid puzzles: {valid} ({valid/total*100:.1f}%)")
            print(f"  Invalid puzzles: {invalid} ({invalid/total*100:.1f}%)")
            print(f"  Output: {output_file}")
            
        except Exception as e:
            print(f"  Error processing {csv_file.name}: {e}")
    
    print("\n" + "=" * 60)
    print("Overall Statistics:")
    print("-" * 60)
    print(f"  Total rows processed: {total_stats['total']}")
    print(f"  Total valid puzzles: {total_stats['valid']} ({total_stats['valid']/total_stats['total']*100:.1f}%)")
    print(f"  Total invalid puzzles: {total_stats['invalid']} ({total_stats['invalid']/total_stats['total']*100:.1f}%)")
    print(f"\nValidated files saved to: {output_dir}/")


def validate_single_csv(
    csv_path: str,
    output_path: str = None,
    puzzle_column: int = 0,
    validate_solution: bool = False,
    answer_column: int | None = None,
):
    """
    Validate a single CSV file.
    
    Args:
        csv_path: Path to the CSV file to validate
        output_path: Path for the output file (default: validated_{filename})
        puzzle_column: Column index containing puzzle data
        validate_solution: If True, validate solutions (completed puzzles). If False, validate puzzles.
        answer_column: Optional column index containing a full solution string.
    """
    
    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        return
    
    if output_path is None:
        base_name = os.path.basename(csv_path)
        # place output in same directory as input
        dir_name = os.path.dirname(csv_path) or "."
        output_path = os.path.join(dir_name, f"validated_{base_name}")
    
    print(f"Validating: {csv_path}")
    print("-" * 60)
    
    try:
        total, valid, invalid = clean_csv(
            csv_path,
            output_path,
            puzzle_column,
            validate_solution,
            answer_column,
        )
        
        print(f"Results:")
        print(f"  Total rows: {total}")
        print(f"  Valid puzzles: {valid} ({valid/total*100:.1f}%)")
        print(f"  Invalid puzzles: {invalid} ({invalid/total*100:.1f}%)")
        print(f"\nOutput saved to: {output_path}")
        
    except Exception as e:
        print(f"Error during validation: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate sudoku puzzles and/or solutions in CSV files."
    )
    subparsers = parser.add_subparsers(dest="mode")

    # single-file mode
    single = subparsers.add_parser("single", help="Validate a single CSV file")
    single.add_argument("csv_file", help="Path to the CSV file to validate")
    single.add_argument(
        "output_file",
        nargs="?",
        help="Where to save the validated file (defaults to same folder with validated_ prefix)",
    )
    single.add_argument(
        "--puzzle-column", "-p", type=int, default=0, help="Column index of the puzzle"
    )
    single.add_argument(
        "--solution", "-s", action="store_true", help="Treat puzzle column as complete solution"
    )
    single.add_argument(
        "--answer", "-a", type=int, help="Column index containing the full solution"
    )
    single.add_argument(
        "--inplace", action="store_true", help="Remove invalid rows from the file instead of writing a new one"
    )

    # batch mode
    batch = subparsers.add_parser("batch", help="Validate all CSVs in a directory")
    batch.add_argument(
        "--data-dir", "-d", default="../data", help="Directory with CSV files"
    )
    batch.add_argument(
        "--output-dir", "-o", help="Where to write validated files (defaults to data-dir)"
    )
    batch.add_argument(
        "--puzzle-column", "-p", type=int, default=0, help="Column index of puzzle"
    )
    batch.add_argument(
        "--solution", "-s", action="store_true", help="Treat puzzle column as complete solution"
    )
    batch.add_argument(
        "--answer", "-a", type=int, help="Column index containing the full solution"
    )
    args = parser.parse_args()

    if args.mode == "single":
        if args.inplace:
            # modify the file directly
            kept, removed = filter_csv_inplace(
                args.csv_file,
                puzzle_column=args.puzzle_column,
                validate_solution=args.solution,
                answer_column=args.answer,
            )
            print(f"Done (in-place). Kept: {kept}, removed: {removed} rows.")
        else:
            validate_single_csv(
                args.csv_file,
                args.output_file,
                args.puzzle_column,
                args.solution,
                args.answer,
            )
    else:
        # default to batch if no subcommand provided
        if getattr(args, "inplace", False):
            data_dir = args.data_dir if hasattr(args, "data_dir") else "../data"
            data_path = Path(data_dir)
            csv_files = list(data_path.glob("*.csv"))
            for csv_file in csv_files:
                print(f"\nProcessing (inplace): {csv_file.name}")
                filter_csv_inplace(
                    str(csv_file),
                    puzzle_column=args.puzzle_column,
                    validate_solution=args.solution,
                    answer_column=args.answer,
                )
        else:
            validate_all_csvs(
                data_dir=args.data_dir if hasattr(args, "data_dir") else "../data",
                output_dir=getattr(args, "output_dir", None),
                validate_solution=getattr(args, "solution", False),
                answer_column=getattr(args, "answer", None),
            )

