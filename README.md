## Overview

This project explores how different search strategies and constraint satisfaction techniques affect the performance of a Sudoku solver. Starting from a naive backtracking approach, the project progressively adds heuristics such as MRV (Minimum Remaining Values) and LCV (Least Constraining Value), and evaluates their impact on solving efficiency.

The codebase is structured to support multiple solver implementations, a benchmarking system to compare performance across puzzles, and a visualization tool to observe the solving process step-by-step. 

## Problem Framing

Sudoku can be modeled as a Constraint Satisfaction Problem (CSP): each cell is a variable, and constraints enforce that values do not repeat within rows, columns, or subgrids.
Despite the simplicity of the rules, the search space grows rapidly. This makes Sudoku a useful testbed for comparing search strategies, where small changes in variable or value selection can lead to significant differences in performance.

<p align="center">
  <img src="assets/sudoku_as_csp.png" alt="Sudoku CSP Diagram" width="600"/>
</p>

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

Median values show that most puzzles are solved quickly, while a smaller number of difficult instances dominate the average runtime.

Despite a dramatic reduction in explored nodes (over 30× with MRV), runtime remains similar across solvers.  
This is primarily due to an implementation tradeoff: domain values are recomputed at every step, introducing significant overhead that offsets the gains from smarter search strategies.

---

## Key Insights

- **Search space reduction is significant with heuristics**  
  MRV reduces explored nodes by more than 30× compared to naive backtracking, confirming that variable selection strongly impacts search efficiency.

- **Runtime is not solely determined by search size**  
  Even with far fewer nodes, MRV does not outperform naive backtracking in runtime. The cost of repeatedly computing domains reduces the expected gains.

- **LCV improves decision quality, not runtime**  
  LCV further reduces backtracking and explored nodes, but does not significantly affect execution time. Its benefit is in guiding the search more effectively rather than speeding it up.

- **Forward checking adds pruning at a cost**  
  While forward checking slightly reduces the search space, it introduces additional computation overhead. In this implementation, the cost outweighs the benefit.

- **Computation vs search is the core tradeoff**  
  These results highlight a key principle: reducing the search space is not enough — the cost of maintaining and evaluating constraints must also be efficient.

---

## Implementation Note

In this implementation, domains (valid values for each cell) are recomputed from scratch at every step rather than maintained incrementally.

This simplifies the design but introduces substantial overhead, particularly for MRV, LCV, and forward checking, which depend heavily on domain evaluation. As a result, improvements in search efficiency do not fully translate into runtime gains.

A more optimized approach would maintain domains incrementally and propagate updates during the search.  
This would eliminate redundant computations and is expected to significantly improve runtime performance, bringing it closer to the theoretical advantages of these heuristics.


## Visual Comparison
### Naive Solver — 262 moves, ~34 seconds
![Naive Solver](assets/naive_solver_gui.gif)

### CSP Solver — 48 moves, ~7 seconds
![CSP Solver](assets/csp_solver_gui.gif)

The naive solver explores many unnecessary branches, repeatedly revisiting invalid paths.
In contrast, the CSP-based solver focuses on constrained regions early,
resulting in a more directed and efficient search.

## Takeaways

- Heuristics like MRV and LCV drastically reduce the search space
- Runtime performance depends heavily on implementation details
- Efficient state management (e.g., incremental domain updates) is critical in CSP solvers
- Visualization helps reveal how different strategies explore the search space

## How To Run:

### 1. Clone the repository
```bash
git clone https://github.com/EdenH442/sudoko-solver.git
cd Sudoko-Solver
```

### 2. Install dependencies
```bash
python -m pip install pygame
```

### 3. Run the GUI
```bash
python -m gui.gui
```

### 4. Run benchmarks
```bash
python -m benchmark.run_benchmark --solver naive --limit 5  --output results/your_output_file.csv
```

### Requirements
- Python 3.10+ (recommended: Python 3.12)

## Future Improvements

- **Incremental domain tracking**  
  Avoid recomputing domains every step to reduce overhead and improve runtime.

- **Stronger constraint propagation (e.g., AC-3)**  
  Detect conflicts earlier and further reduce the search space.