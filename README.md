# A-Maze-Ing

A maze generator and solver using DFS and Prim's algorithms.

## Maze Generator Module Documentation

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic Usage

```python
import random
from mazegenerator.mazegenerator import MazeGenerator

# Define maze parameters
config = {
    'WIDTH': 10,
    'HEIGHT': 10,
    'SEED': 42,
    'PERFECT': True,
    'ENTRY': (0, 0),
    'EXIT': (9, 9),
    'ALGO': 'dfs',
    'OUTPUT_FILE': 'maze.txt',
}

# Set the random seed
random.seed(config['SEED'])

# Instantiate the generator
maze = MazeGenerator(config)

# Generate the maze using DFS (without animation)
maze.dfs_algo()

# Access the maze grid structure (2D list of wall bitmask values)
print(maze.grid)       # e.g. [[6, 12, ...], ...]
print(maze.width)      # 10
print(maze.height)     # 10

# Solve the maze using BFS
path = maze.solve_bfs(config['ENTRY'], config['EXIT'])
print(path)  # e.g. [(0,0), (1,0), (1,1), ..., (9,9)]
```

### Custom Parameters

| Parameter   | Type           | Description                                |
|-------------|----------------|--------------------------------------------|
| `WIDTH`     | `int`          | Number of columns in the maze              |
| `HEIGHT`    | `int`          | Number of rows in the maze                 |
| `SEED`      | `int` or `None`| Random seed for reproducibility            |
| `PERFECT`   | `bool`         | `True` for perfect maze, `False` to remove extra walls |
| `ENTRY`     | `tuple(x, y)`  | Entry cell coordinates                     |
| `EXIT`      | `tuple(x, y)`  | Exit cell coordinates                      |
| `ALGO` | `str`          | `"dfs"` or `"prim"`                        |
| `OUTPUT_FILE`| `str`         | Path for the output file                   |

### Using Prim's Algorithm

```python
from mazegenerator.primalgo import PrimGenerator

maze = PrimGenerator(config)
maze.prim_algo()  # Generate using Prim's algorithm
```

### Accessing the Maze Structure

Each cell in `maze.grid[y][x]` is an integer bitmask (0–15) representing walls:

- `1` (NORTH) — top wall
- `2` (EAST) — right wall
- `4` (SOUTH) — bottom wall
- `8` (WEST) — left wall

A value of `15` means all four walls are present. A value of `0` means no walls.

### Getting a Solution

```python
path = maze.solve_bfs((0, 0), (9, 9))
# Returns a list of (x, y) tuples from entry to exit
# Returns an empty list if no path exists
```

### Building the Package

```bash
pip install build
python3 -m build
```

This creates `mazegen-1.0.0.tar.gz` and `mazegen-1.0.0-py3-none-any.whl` in the `dist/` directory.
