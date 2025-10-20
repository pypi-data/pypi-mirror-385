# FMI AI Judge — CLI System

[![PyPI - Version](https://img.shields.io/pypi/v/fmi-ai-judge)](https://pypi.org/project/fmi-ai-judge/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fmi-ai-judge)](https://pypi.org/project/fmi-ai-judge/)
[![License](https://img.shields.io/badge/License-BSD--3--Clause-lightgrey.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-cross--platform-brightgreen.svg)](#)
<!-- [![Build](https://github.com/BorisVelichkov/fmi-ai-judge/actions/workflows/ci.yml/badge.svg)](https://github.com/BorisVelichkov/fmi-ai-judge/actions) -->
<!-- [![TestPyPI](https://img.shields.io/badge/TestPyPI-fmi--ai--judge-informational)](https://test.pypi.org/project/fmi-ai-judge/) -->

CLI to run AI homework solutions against official tests (Frog-Leap, N-Puzzle, N-Queens, TSP, Knapsack).  
Cross-language: Python/Node/Ruby/PHP/Julia/PowerShell/Bash, Java (.jar/.class), .NET (.dll), native executables.  
Created for the **AI course** at the **Faculty of Mathematics and Informatics, Sofia University**.

## Install
```bash
pip install fmi-ai-judge
```

## Quick start
```bash
judge --version

judge list

judge run --bench path/to/solution.py
judge run --bench path/to/folder/*.py
judge run --bench path/to/folder/*
judge run --bench path/to/folder/

# If auto-detection fails, force the problem id/alias:
judge run --bench -p n-queens path/to/solver.py
```

## CLI (help)
```bash
judge list                       # list problems & aliases
judge run [OPTIONS] PATH [...]   # run one or more programs

Options:
  -p, --problem ID     Force problem id/alias (e.g., n-queens, frog-leap)
  --exec "CMD {src}"   Override runner (e.g., "python {src}", "java -jar {src}")
  --slow               Use slow tier timing for all programs
  --bench              Parse "# TIMES_MS: alg=<ms>" from stdout
  --out DIR            Artifacts dir (default: .judge)
```

## Output & timing
Report columns: `problem  test  status  time(ms)  limit  alg(ms)  cal(ms)  note`
- `alg(ms)` is parsed only with `--bench` and a header like `# TIMES_MS: alg=123`.
- Calibration adds small I/O slack: **fast +25ms**, **slow +200ms**.
- Artifacts: `.judge/results.json` and `.judge/results.csv`.

## Problems (formats)

**Optional timing header (all problems).**  
Student output may start with a timing line:
```bash
# TIMES_MS: alg=<milliseconds>
```
It’s ignored unless you run with `--bench`, in which case it’s parsed as the algorithm time.

### Frog-Leap (DFS)
The input is a number `n`. The output is a solution consisting of `(n+1)²` lines, starting from the initial state and ending at the goal. Each move is a single or double jump - onto the next empty leaf or over one opposite frog onto an empty leaf. States are printed using `>`, `<`, `_`.

#### Example:
- **Input**
    ```bash
    2
    ```
- **Output**  
    ```bash
    >>_<<
    >_><<
    ><>_<
    ><><_
    ><_<>
    _<><>
    <_><>
    <<>_>
    <<_>>
    ```

### N-Puzzle (IDA\*)
The input starts with the puzzle size (`8`, `15`, `24`, etc.), followed by the index of the empty space (marked with `0`) in the solution - `0` for the first position, `n/2` for the center (in odd puzzles), and either `n-1` or `-1` for the last position (both are equivalent). Then follow `√(n+1)` lines, each containing `√(n+1)` numbers representing the puzzle state. The output prints `K`, the optimal number of steps to reach the solution, followed by exactly `K` moves (`left`, `right`, `up`, or `down`), or `-1` if unsolvable. Optimality must be enforced when an optimal length is provided in the `.out` file.

#### Example:
- **Input**
    ```bash
    8
    -1
    1 2 3
    4 5 6
    0 7 8
    ```
- **Output**  
    ```bash
    2
    left
    left
    ```

### N-Queens (min-conflicts)
The input is a positive integer `n` (up to `10,000 ±10`).  
Output `-1` when **`n ∈ {2,3}`**; otherwise print a one-dimensional representation of a solution as a permutation where each index is a column and each value is the row of the queen (0- or 1-based accepted), e.g. `[2, 0, 3, 1]`. The output may be a simple list of values rather than strict array notation.

#### Example:
- **Input**
    ```bash
    4
    ```
- **Output**  
    ```bash
    [2, 0, 3, 1]
    ```

### Traveling Salesman Problem, TSP (GA)
The input is either:
1. A single number `n` (`n ≤ 100`) — the number of cities to be generated randomly in a 2D space, or
2. A dataset name (e.g., `UK12`), followed by the number of cities and their names with coordinates.

The program searches for short routes using a **genetic algorithm**.

For **random N points**: print ≥10 **non-increasing** distances (one per line), a **blank line**, then the **final distance** (must equal the last value). *(No path line in the random case.)*

For **named datasets**: print the same distances block, a **blank line**, then
`CityA -> CityB -> ...`, and the **final distance** (must equal both the recomputed **open-path** length and the **last** value).

Optimality should match a sibling `.out` file when present; otherwise a known reference may be used for specific datasets (e.g., `UK12`). Small float tolerances apply.

#### Example:
- **Input**
    ```bash
    UK12
    12
    Aberystwyth       0.190032E-03    -0.285946E-03
    Brighton        383.458           -0.608756E-03
    Edinburgh       -27.0206        -282.758
    Exeter          335.751         -269.577
    Glasgow          69.4331        -246.780
    Inverness       168.521           31.4012
    Liverpool       320.350         -160.900
    London          179.933         -318.031
    Newcastle       492.671         -131.563
    Nottingham      112.198         -110.561
    Oxford          306.320         -108.090
    Stratford       217.343         -447.089
    ```
- **Output**  
    ```bash
    2426.8086
    2396.0235
    2268.7090
    2231.2278
    2111.5853
    1969.2157
    1659.4007
    1659.4007
    1595.7385
    1595.7385

    Aberystwyth -> Inverness -> Nottingham -> Glasgow -> Edinburgh -> London -> Stratford -> Exeter -> Liverpool -> Oxford -> Brighton -> Newcastle
    1595.7385
    ```

### Knapsack (GA)
The input starts with two numbers: the knapsack capacity `m` and the number of items `n` (`n < 10,000`), followed by `n` lines each containing an item’s weight `mi` and value `ci`. The program uses a **genetic algorithm** to maximize the total value without exceeding capacity `m`. The output lists at least 10 values of the best solution (first, several intermediate, and last generations), followed by a blank line, then the final maximum value. Optimality should match the provided `.out` file or reference data when available.

#### Example:
- **Input**
    ```bash
    5000 24
    90 150
    130 35
    1530 200
    500 160
    150 60
    680 45
    270 60
    390 40
    230 30
    520 10
    110 70
    320 30
    240 15
    480 10
    730 40
    420 70
    430 75
    220 80
    70 20
    180 12
    40 50
    300 10
    900 1
    2000 150
    ```
- **Output**  
    ```bash
    1010
    1130
    1130
    1130
    1130
    1130
    1130
    1130
    1130
    1130

    1130
    ```

## Repeats & optimality
Per-test in `tests.yaml`:
- `repeats` / `min_success` (e.g., stochastic GA).
- `require_optimal: true` → a non-optimal OK is turned into **WA** by the CLI.

## Problem discovery
Auto-infers from filename/aliases; override with `--problem`. Aliases live in `fmi_ai_judge/problems.yaml`.

## Contributing
See `CONTRIBUTING.md`. Changes are tracked in `CHANGELOG.md`.

## License
BSD-3-Clause.

