*This project has been created as part of the 42 curriculum by mokarimi and yboukhmi.*

# A-Maze-Ing

## Description

A maze generator and solver in Python. It reads a configuration file, generates a maze
using DFS or Prim's algorithm, solves it with BFS, displays it in the terminal with
animation, and writes the result to a file.

## Instructions

### Installation

```bash
make install
```

### Execution

```bash
python3 a_maze_ing.py config.txt
```

### Other commands

```bash
make debug        # Run with debugger
make lint         # Flake8 + mypy
make lint-strict  # Flake8 + mypy --strict
make build        # Build and install package
make clean        # Remove caches and output files
```

## Config File Format

Plain text file with one `KEY=VALUE` per line. Lines starting with `#` are comments.

| Key | Required | Type | Description |
| --- | --- | --- | --- |
| `WIDTH` | Yes | Integer (9–200) | Maze width |
| `HEIGHT` | Yes | Integer (7–200) | Maze height |
| `ENTRY` | Yes | `x,y` | Entry coordinates |
| `EXIT` | Yes | `x,y` | Exit coordinates |
| `OUTPUT_FILE` | Yes | Path (`.txt`) | Output file |
| `PERFECT` | Yes | `True` / `False` | Perfect maze or not |
| `ALGO` | No | `dfs` / `prim` | Generation algorithm (default: dfs) |
| `SEED` | No | Integer | Random seed |

### Example

```ini
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,19
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=45
ALGO=dfs
```

## Maze Generation Algorithms

### DFS (default)

Uses a stack to visit random unvisited neighbors, removes walls while progressing,
and backtracks at dead ends.

### Prim's Algorithm

Starts from one cell, tracks frontier walls, and grows the maze by connecting random
frontier cells to the existing area.

## Why DFS as Default

- Simple to implement and explain.
- Produces long corridors that look visually clear.
- Integrates naturally with stack-based animation.

Prim was added for algorithmic variety and a different maze style.

## Reusable Code

The `mazegenerator/` module is a standalone package installable via the built
`mazegen-1.0.0.tar.gz` at the root of the repository.

### How to use it

```python
from mazegenerator.mazegenerator import MazeGenerator

config = {
    'WIDTH': 20, 'HEIGHT': 20,
    'ENTRY': (0, 0), 'EXIT': (19, 19),
    'OUTPUT_FILE': 'maze.txt',
    'PERFECT': True, 'SEED': 42,
}
gen = MazeGenerator(config)
gen.set_42()
gen.dfs_algo()
path = gen.solve_bfs(config['ENTRY'], config['EXIT'])
gen.write_to_file(config['OUTPUT_FILE'], path)
```

You can pass custom parameters (size, seed, algorithm) through the config dict.
Access the generated structure via `gen.grid` and the solution via `solve_bfs()`.

### Rebuilding the package

```bash
make install
make build
```

## Advanced Features

- Two generation algorithms (DFS and Prim).
- Terminal animation during generation.
- Solved-path animation.
- Interactive menu: regenerate, toggle path, rotate colors, quit.
- Imperfect maze mode (`PERFECT=False`).
- Centered `42` reserved pattern.

## Team and Project Management

### Roles

- `mokarimi`: Prim's algorithm, terminal display, animation.
- `yboukhmi`: DFS generation, BFS solving, configuration parsing.

### Planning

1. Parse and validate config.
2. Implement maze structure and DFS.
3. Add BFS solving.
4. Export to file.
5. Add terminal display and animation.
6. Add Prim's algorithm and interactive menu.
7. Clean code and write documentation.

### How it evolved

- Prim was added as a second generator.
- Display grew into an animated viewer with a menu.
- The `42` pattern became part of generation constraints.

### What worked well

- Separation between parsing, generation, display, and export.
- Reusing the same maze structure for both algorithms.

### What could be improved

- Display code could be split further.
- Automated tests could be expanded.

### Tools used

Python, curses, make, poetry, flake8, mypy, Git.

## Resources

- [Python docs](https://docs.python.org/3/)
- [curses docs](https://docs.python.org/3/library/curses.html)
- [DFS](https://en.wikipedia.org/wiki/Depth-first_search)
- [BFS](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Prim's algorithm](https://en.wikipedia.org/wiki/Prim%27s_algorithm)

### AI Usage

AI was used for reviewing documentation, adding comments, checking style issues,
and helping rewrite the README. It was not used to replace understanding of the
algorithms or project structure.
