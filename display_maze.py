import curses
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mazegenerator import MazeGenerator

N, E, S, W = 1, 2, 4, 8
DIRECTIONS = {N: (0, -1), S: (0, 1), E: (1, 0), W: (-1, 0)}

# Display cell types
WALL = 0
PASSAGE = 1
RESERVED = 2
ENTRY_T = 3
EXIT_T = 4
PATH = 5





class SimpleDisplay:
    """Minimal maze renderer — walls, passages, and reserved (42) cells."""

    def __init__(self, maze_gen: 'MazeGenerator', path: list[tuple[int, int]]) -> None:
        self.path = path
        self.maze = maze_gen
        self.reserved: set[tuple[int, int]] = getattr(maze_gen, 'reserved', set())

    def _cell_type(self, x: int, y: int) -> int:
        entry = self.maze.config['ENTRY']
        exit = self.maze.config['EXIT']
        if (x, y) == entry:
            return ENTRY_T
        if (x, y) == exit:
            return EXIT_T
        if (x, y) in self.path:
            return PATH
        if (x, y) in self.reserved:
            return RESERVED
        return PASSAGE

    def _build_display(self) -> list[list[int]]:
        """Build a (2H+1) x (2W+1) grid: WALL, PASSAGE, or RESERVED."""
        h = self.maze.height
        w = self.maze.width
        grid = self.maze.grid
        rows = 2 * h + 1
        cols = 2 * w + 1

        disp = [[WALL] * cols for _ in range(rows)]

        # Cell interiors
        for y in range(h):
            for x in range(w):
                disp[2 * y + 1][2 * x + 1] = self._cell_type(x, y)

        # Internal edges
        path_nodes = (PATH, ENTRY_T, EXIT_T)
        for y in range(h):
            for x in range(w):
                cell = grid[y][x]
                if x + 1 < w and not (cell & E):
                    t1 = self._cell_type(x, y)
                    t2 = self._cell_type(x + 1, y)
                    if t1 == RESERVED and t2 == RESERVED:
                        disp[2 * y + 1][2 * (x + 1)] = RESERVED
                    elif t1 in path_nodes and t2 in path_nodes:
                        disp[2 * y + 1][2 * (x + 1)] = PATH
                    else:
                        disp[2 * y + 1][2 * (x + 1)] = PASSAGE
                if y + 1 < h and not (cell & S):
                    t1 = self._cell_type(x, y)
                    t2 = self._cell_type(x, y + 1)
                    if t1 == RESERVED and t2 == RESERVED:
                        disp[2 * (y + 1)][2 * x + 1] = RESERVED
                    elif t1 in path_nodes and t2 in path_nodes:
                        disp[2 * (y + 1)][2 * x + 1] = PATH
                    else:
                        disp[2 * (y + 1)][2 * x + 1] = PASSAGE

        # Border openings (entry / exit holes) lbiban dyal jnab 
        for y in range(h):
            for x in range(w):
                cell = grid[y][x]
                ct = self._cell_type(x, y)
                if y == 0 and not (cell & N):
                    disp[0][2 * x + 1] = ct
                if y == h - 1 and not (cell & S):
                    disp[2 * h][2 * x + 1] = ct
                if x == 0 and not (cell & W):
                    disp[2 * y + 1][0] = ct
                if x == w - 1 and not (cell & E):
                    disp[2 * y + 1][2 * w] = ct

        # Fix corners surrounded by non-walls
        for dy in range(rows):
            for dx in range(cols):
                if dy % 2 == 0 and dx % 2 == 0 and disp[dy][dx] == WALL:
                    adj_types = []
                    all_open = True
                    for ady, adx in [(dy - 1, dx), (dy + 1, dx),
                                     (dy, dx - 1), (dy, dx + 1)]:
                        if 0 <= ady < rows and 0 <= adx < cols:
                            if disp[ady][adx] == WALL:
                                all_open = False
                                break
                            adj_types.append(disp[ady][adx])
                        else:
                            all_open = False
                            break
                    if all_open and adj_types:
                        if all(t == RESERVED for t in adj_types):
                            disp[dy][dx] = RESERVED
                        else:
                            disp[dy][dx] = PASSAGE

        return disp

    def _init_colors(self) -> None:
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        # Gray for 42 cells
        if curses.COLORS >= 256:
            gray = 245
        elif curses.can_change_color():
            curses.init_color(8, 500, 500, 500)
            gray = 8
        else:
            gray = curses.COLOR_WHITE

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)  # walls
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)                               # 42 cells
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_GREEN) # ENTRY
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)     # EXIT
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_YELLOW)  # PATH

    def _draw_frame(self, stdscr: curses.window) -> int:
        type_to_pair = {
            WALL: 1,
            PASSAGE: 0,
            RESERVED: 2,
            ENTRY_T: 3,
            EXIT_T: 4,
            PATH: 5
        }

        stdscr.clear()
        display = self._build_display()
        rows = len(display)

        for dy in range(rows):
            for dx in range(len(display[dy])):
                pair = type_to_pair.get(display[dy][dx], 0)
                try:
                    stdscr.addstr(dy, dx * 2, "  ", curses.color_pair(pair))
                except curses.error:
                    pass
        return rows

    def draw(self, stdscr: curses.window) -> None:
        self._init_colors()
        rows = self._draw_frame(stdscr)
        
        try:
            stdscr.addstr(rows + 1, 0, "Press any key to quit.")
        except curses.error:
            pass

        stdscr.refresh()
        stdscr.getch()

    def animate_draw(self, stdscr: curses.window, delay: float = 0.2) -> None:
        self._init_colors()

        original_path = list(self.path)
        self.path = []

        rows = 0
        for cell in original_path:
            self.path.append(cell)
            rows = self._draw_frame(stdscr)

            stdscr.refresh()
            curses.napms(int(delay * 1000))

        try:
            stdscr.addstr(rows + 2, 0, "Done. Press any key to quit.")
        except curses.error:
            pass

        stdscr.refresh()
        stdscr.getch()

def render_maze(maze_gen: 'MazeGenerator', path: list[tuple[int, int]]) -> None:
    """Simple display — just renders the maze grid, no extras."""
    sd = SimpleDisplay(maze_gen, path)
    curses.wrapper(sd.draw)

def animate_maze(maze_gen: 'MazeGenerator', path: list[tuple[int, int]], delay: float = 0.08) -> None:
    """Animate the solution path."""
    sd = SimpleDisplay(maze_gen, path)
    curses.wrapper(lambda stdscr: sd.animate_draw(stdscr, delay))

def draw_generation_frame(stdscr: curses.window, maze_gen: 'MazeGenerator') -> None:
    sd = SimpleDisplay(maze_gen, path=[])
    sd._init_colors()
    sd._draw_frame(stdscr)
    stdscr.refresh()

def animate_generation(maze_gen: 'MazeGenerator', algo: str = "dfs", delay: int = 20) -> None:
    curses.wrapper(lambda stdscr: _run_generation(stdscr, maze_gen, algo, delay))


def _run_generation(stdscr: curses.window, maze_gen: Any, algo: str, delay: int) -> None:
    curses.curs_set(0)

    if algo == "dfs":
        maze_gen.dfs_algo(stdscr=stdscr, animate=True, delay=delay)
    elif algo == "prim":
        maze_gen.prim_algo(stdscr=stdscr, animate=True, delay=delay)
    else:
        raise ValueError("algo must be 'dfs' or 'prim'")

    draw_generation_frame(stdscr, maze_gen)

    try:
        sd = SimpleDisplay(maze_gen, path=[])
        rows = len(sd._build_display())
        stdscr.addstr(rows + 1, 0, "Press any key to continue.")
    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()