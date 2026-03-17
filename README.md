*This project has been created as part of the 42 curriculum by mokarimi and yboukhmi.*

# A-Maze-Ing

## Description

A-Maze-Ing is a Python project that generates, displays, solves, and exports mazes.
Its goal is to build a complete maze pipeline: read a configuration file, validate the
input, generate a maze with a chosen algorithm, solve it with BFS, display it in the
terminal with animation, and write the final result to a text file.

The project supports:

- Two generation algorithms: DFS and Prim.
- Terminal animation with `curses`.
- A solved-path visualization.
- An optional imperfect maze mode.
- Export of the generated maze and solution path.
- A centered reserved `42` pattern inside the maze.

## Project Structure

- [`a_maze_ing.py`]: program entry point.
- [`mazegenerator/config_parser.py`]:  configuration parsing and validation.
- [`mazegenerator/mazegenerator.py`]:  core maze representation, DFS generation, BFS solving, and file export.
- [`mazegenerator/primalgo.py`]:  Prim-based generator.
- [`mazegenerator/display_maze.py`]:  terminal rendering, animation, and interactive menu.
- [`mazegenerator/maze_animation.py`]: shared generation animation step.
- [`config.txt`]: example configuration file.
- [`Makefile`]: helper commands.

## Instructions

### Requirements

- Python 3.10 or newer
- A terminal that supports `curses`

### Installation

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Or use the provided Make target:

```bash
make install
```

### Execution

Run the project with a config file:

```bash
python3 a_maze_ing.py config.txt
```

Or:

```bash
make run
```

### Debug and Quality Commands

```bash
make debug
make lint
make lint-strict
make build
```

## Config File Format

The project expects a plain text config file with one `KEY=VALUE` pair per line.
Empty lines and lines starting with `#` are ignored.

### Supported keys

| Key | Required | Type | Description |
| --- | --- | --- | --- |
| `WIDTH` | Yes | Integer | Maze width |
| `HEIGHT` | Yes | Integer | Maze height |
| `ENTRY` | Yes | `x,y` | Entry coordinates |
| `EXIT` | Yes | `x,y` | Exit coordinates |
| `OUTPUT_FILE` | Yes | Path ending in `.txt` | Output file |
| `PERFECT` | Yes | `True` or `False` | Perfect or imperfect maze |
| `ALGO` | No | `dfs` or `prim` | Generation algorithm |
| `SEED` | No | Integer | Random seed for reproducibility |

### Validation rules

- `WIDTH` and `HEIGHT` must be integers.
- Minimum maze size is `9x7`.
- Maximum maze size is `200x200`.
- `ENTRY` and `EXIT` must be inside maze bounds.
- `ENTRY` and `EXIT` cannot be the same.
- `OUTPUT_FILE` must end with `.txt`.
- `PERFECT` must be `True` or `False`.
- `ALGO` must be `dfs` or `prim`.
- `SEED` is optional.

### Example config

```ini
WIDTH=20
HEIGHT=20

# Start at top-left, end at bottom-right
ENTRY=0,0
EXIT=19,19

OUTPUT_FILE=maze.txt
PERFECT=False
SEED=45
ALGO=dfs
```

## Maze Generation Algorithm

This project supports two maze generation algorithms:

### 1. Depth-First Search (DFS)

It uses a stack, visits unvisited neighbors, removes walls while progressing, and
backtracks when it reaches a dead end.

### 2. Prim's Algorithm

It starts from one cell, tracks frontier walls, and grows the maze by connecting random
frontier cells to the existing carved area.

## Chosen Algorithm and Why

The project includes both algorithms as an advanced feature, but DFS is the default
choice in the parser and sample config.

DFS was chosen as the default because:

- It is simple to implement and explain.
- It produces long, winding corridors that make the maze visually clear.
- It integrates naturally with stack-based animation.
- It is a common reference algorithm for maze generation, which makes the project easier
  to present and evaluate.

Prim was added because:

- It gives a different maze style.
- It demonstrates algorithmic variety.
- It makes the project more reusable and more complete technically.

## Solving Strategy

The generated maze is solved with Breadth-First Search (BFS), which returns a path from
`ENTRY` to `EXIT`. BFS was chosen because it is straightforward and guarantees the
shortest path in an unweighted grid graph.

## Advanced Features

The repository contains several advanced or extra features:

- Multiple generation algorithms: DFS and Prim.
- Terminal animation during generation.
- Solved-path animation after generation.
- Interactive menu for regenerating the maze, toggling the path, and rotating color
  themes.
- Imperfect maze mode by removing extra walls after generation.
- Reserved centered `42` pattern.

If these features are enabled, they are reflected by:

- `ALGO=dfs` or `ALGO=prim`
- `PERFECT=True` or `PERFECT=False`
- animated display through the terminal UI

## Reusable Parts of the Code

Several parts of this project are reusable outside this specific executable:

- `MazeGenerator` can be reused as a general grid-based maze engine.
- `PrimGenerator` adds an alternative generation strategy without changing the rest of
  the pipeline.
- `ConfigPasrer` can be reused as a simple validated config loader for key-value files.
- `solve_bfs()` can be reused as a generic shortest-path solver on the maze structure.
- `SimpleDisplay` can be reused to render maze states in a terminal application.
- `write_to_file()` can be reused to export mazes in the project output format.

This separation makes it possible to reuse the code in:

- other terminal-based maze projects
- algorithm comparison projects
- teaching demos for DFS, BFS, and Prim
- future GUI or web frontends that keep the same maze core

## Output Format

The generated output file contains:

1. The maze grid as hexadecimal values, one row per line.
2. An empty line.
3. The entry coordinates.
4. The exit coordinates.
5. The solution path as direction letters (`N`, `S`, `E`, `W`).

## Team and Project Management

### Team roles

This project was developed by a two-member team:

- `mokarimi`: Prim's algorithm, terminal display, and animation.
- `yboukhmi`: DFS generation, BFS solving, and configuration parsing.

### Anticipated planning

The initial plan was:

1. Parse and validate the config file.
2. Implement the maze data structure and DFS generation.
3. Add solving with BFS.
4. Export the result to a file.
5. Add terminal display and animation.
6. Add extra features such as another algorithm and interaction.
7. Clean the codebase and write documentation.

### How the plan evolved

The project evolved from a core generator/solver into a more complete terminal
application:

- Prim's algorithm was added as a second generator.
- The display layer grew into an animated viewer with a menu.
- The centered `42` reserved pattern became part of the generation constraints.
- Documentation and code comments were expanded later to improve maintainability.

### What worked well

- The separation between parsing, generation, display, and export made the code easier
  to extend.
- Reusing the same maze structure for both DFS and Prim reduced duplication.
- BFS fit cleanly on top of the generated graph representation.

### What could be improved

- `curses` display code could be split further to reduce file size and improve clarity.
- Some naming and class organization could be tightened.
- Automated tests could be expanded.
- A formal `flake8`/CI setup would make validation easier.

### Tools used

- Python
- `curses`
- `make`
- `poetry`
- `flake8`
- `mypy`
- Git

## Resources

### Classic references

- Python documentation: https://docs.python.org/3/
- `curses` documentation: https://docs.python.org/3/library/curses.html
- Breadth-First Search overview:
  https://en.wikipedia.org/wiki/Breadth-first_search
- Depth-First Search overview:
  https://en.wikipedia.org/wiki/Depth-first_search
- Prim's algorithm overview:
  https://en.wikipedia.org/wiki/Prim%27s_algorithm

### AI usage

AI was used as an assistant for:

- reviewing and improving documentation
- adding and refining docstrings/comments
- checking style issues such as line length and formatting
- helping rewrite the README to match the requested specification

AI was not used to replace understanding of the algorithms or the overall project
structure; it was used mainly as a support tool for writing, review, and cleanup.
