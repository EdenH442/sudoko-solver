## Overview

This project explores how different search strategies and constraint satisfaction techniques effect the performance of a Sudoku solver. Starting from a naive backtracking approach, and progressively adding heuristics such as MRV (Minimum Remaining Values) and LCV (Least Constraining Value), and evaluates their impact on solving efficiency.

The codebase is structured to support multiple solver implementations, a benchmarking system to compare performance across puzzles, and a visualization tool to observe the solving process step-by-step. 

## Problem Framing

Sudoku can be modeled as a Constraint Satisfaction Problem (CSP): each cell is a variable, and constraints enforce that values do not repeat within rows, columns, or subgrids.
Despite the simplicity of the rules, the search space grows rapidly. This makes Sudoku a useful testbed for comparing search strategies, where small changes in variable or value selection can lead to significant differences in performance.

```mermaid
flowchart TD
    A[Sudoku Puzzle] --> B[Variables: empty cells]
    A --> C[Domains: possible values 1-9]
    A --> D[Constraints]

    D --> E[No duplicates in row]
    D --> F[No duplicates in column]
    D --> G[No duplicates in 3x3 subgrid]

    B --> H[Search Strategy]
    C --> H
    D --> H

    H --> I[Naive Backtracking]
    H --> J[MRV]
    H --> K[MRV + LCV]
    H --> L[MRV + Forward Checking]
## Solver Progression

The project follows a progression of increasingly informed search strategies, where each solver builds on the previous one.

### Naive Backtracking
Selects the next empty cell in a fixed order and tries values sequentially.  
This approach is simple and guarantees correctness, but explores a large search space and performs poorly on harder puzzles.

### MRV (Minimum Remaining Values)
Selects the cell with the fewest valid candidates at each step.  
Instead of filling cells in a fixed order, MRV prioritizes the most constrained variables. This increases the chance of detecting conflicts early, reducing unnecessary branching and limiting the size of the search tree.

### MRV + LCV (Least Constraining Value)
Extends MRV by ordering candidate values based on how little they restrict neighboring cells.  
This helps delay conflicts and reduces backtracking.

### MRV + Forward Checking
In this approach, after each assignment, invalid values are removed from neighboring cells.  
This reduces future conflicts but introduces additional overhead, creating a tradeoff between pruning effectiveness and runtime.

## Results

### Average Performance Across All Puzzles

| Solver                | Avg Time (s) | Median Time (s) | Avg Nodes | Avg Backtracks | Avg Assignments |
|---------------------|-------------|-----------------|-----------|----------------|-----------------|
| Naive Backtracking  | 1.15        | 0.46            | 165,040   | 164,984        | 165,039         |
| MRV                 | 1.20        | 0.60            | 5,173     | 5,117          | 5,172           |
| MRV + LCV           | 1.20        | 0.97            | 4,766     | 4,710          | 4,765           |
| MRV + Forward Check | 1.33        | 0.82            | 4,742     | 5,117          | 5,172           |