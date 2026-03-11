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
        self.theme_index = 0

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

        themes = [
            (curses.COLOR_WHITE, curses.COLOR_MAGENTA, curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_YELLOW),
            (curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_WHITE),
            (curses.COLOR_YELLOW, curses.COLOR_MAGENTA, curses.COLOR_CYAN, curses.COLOR_RED, curses.COLOR_GREEN),
        ]

        wall_c, reserved_c, entry_c, exit_c, path_c = themes[self.theme_index % len(themes)]

        curses.init_pair(1, wall_c, wall_c)          # walls
        curses.init_pair(2, reserved_c, reserved_c)  # 42
        curses.init_pair(3, entry_c, entry_c)        # entry
        curses.init_pair(4, exit_c, exit_c)          # exit
        curses.init_pair(5, path_c, path_c)          # path

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
            stdscr.addstr(rows + 2, 0, "=== A-Maze-ing ===")
            stdscr.addstr(rows + 2, 0, "1. Re-generate a new maze")
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

def draw_generation_frame(stdscr: curses.window, maze_gen: 'MazeGenerator', theme_index: int = 0) -> None:
    sd = SimpleDisplay(maze_gen, path=[])
    sd.theme_index = theme_index
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
        stdscr.addstr(rows + 1, 0, "=== A-Maze-ing ===")
        stdscr.addstr(rows + 2, 0, "1. Re-generate a new maze")
    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()

def simple_menu_maze(maze_gen, path, algo="dfs", gen_delay=15):
    curses.wrapper(lambda stdscr: _simple_menu_loop(stdscr, maze_gen, path, algo, gen_delay))


def _simple_menu_loop(stdscr, maze_gen, path, algo, gen_delay):
    curses.curs_set(0)

    full_path = path
    show_path = True
    theme_index = 0

    # path animation first time
    shown_path = []
    for cell in full_path:
        shown_path.append(cell)

        sd = SimpleDisplay(maze_gen, shown_path)
        sd.theme_index = theme_index
        sd._init_colors()
        rows = sd._draw_frame(stdscr)

        try:
            stdscr.addstr(rows + 1, 0, "=== A-Maze-ing ===")
            stdscr.addstr(rows + 2, 0, "1. Re-generate a new maze")
            stdscr.addstr(rows + 3, 0, "2. Show/hide path")
            stdscr.addstr(rows + 4, 0, "3. Rotate maze colors")
            stdscr.addstr(rows + 5, 0, "4. Quit")
        except curses.error:
            pass

        stdscr.refresh()
        curses.napms(50)

    while True:
        sd = SimpleDisplay(maze_gen, full_path if show_path else [])
        sd.theme_index = theme_index
        sd._init_colors()
        rows = sd._draw_frame(stdscr)

        try:
            stdscr.addstr(rows + 1, 0, "=== A-Maze-ing ===")
            stdscr.addstr(rows + 2, 0, "1. Re-generate a new maze")
            stdscr.addstr(rows + 3, 0, "2. Show/hide path")
            stdscr.addstr(rows + 4, 0, "3. Rotate maze colors")
            stdscr.addstr(rows + 5, 0, "4. Quit")
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('1'):
            new_gen = type(maze_gen)(maze_gen.config)

            if hasattr(maze_gen, 'reserved'):
                try:
                    new_gen.set_42()
                except Exception:
                    pass

            # generate with animation
            if algo == "prim" and hasattr(new_gen, "prim_algo"):
                new_gen.prim_algo(stdscr=stdscr, animate=True, delay=gen_delay, theme_index=theme_index)
            elif algo == "dfs" and hasattr(new_gen, "dfs_algo"):
                new_gen.dfs_algo(stdscr=stdscr, animate=True, delay=gen_delay, theme_index=theme_index)
            else:
                raise ValueError("Invalid algorithm choice.")

            full_path = new_gen.solve_bfs(new_gen.config['ENTRY'], new_gen.config['EXIT'])
            maze_gen = new_gen

            # path animation after regenerate
            shown_path = []
            for cell in full_path:
                shown_path.append(cell)

                sd = SimpleDisplay(maze_gen, shown_path if show_path else [])
                sd.theme_index = theme_index
                sd._init_colors()
                rows = sd._draw_frame(stdscr)

                try:
                    stdscr.addstr(rows + 1, 0, "=== A-Maze-ing ===")
                    stdscr.addstr(rows + 2, 0, "1. Re-generate a new maze")
                    stdscr.addstr(rows + 3, 0, "2. Show/hide path")
                    stdscr.addstr(rows + 4, 0, "3. Rotate maze colors")
                    stdscr.addstr(rows + 5, 0, "4. Quit")
                except curses.error:
                    pass

                stdscr.refresh()
                curses.napms(50)

        elif key == ord('2'):
            show_path = not show_path

        elif key == ord('3'):
            theme_index += 1

        elif key == ord('4'):
            break

# import curses
# from typing import TYPE_CHECKING, Any

# if TYPE_CHECKING:
#     from mazegenerator import MazeGenerator

# N, E, S, W = 1, 2, 4, 8

# WALL = 0
# PASSAGE = 1
# RESERVED = 2
# ENTRY_T = 3
# EXIT_T = 4
# PATH = 5

# MENU_LINES = [
#     "=== A-Maze-ing ===",
#     "1. Re-generate a new maze",
#     "2. Show/hide path",
#     "3. Rotate maze colors",
#     "4. Quit",
# ]


# class SimpleDisplay:
#     def __init__(self, maze_gen: "MazeGenerator", path: list[tuple[int, int]] | None = None) -> None:
#         self.maze = maze_gen
#         self.path = path or []
#         self.reserved: set[tuple[int, int]] = getattr(maze_gen, "reserved", set())
#         self.theme_index = 0

#     def _cell_type(self, x: int, y: int) -> int:
#         entry = self.maze.config["ENTRY"]
#         exit_ = self.maze.config["EXIT"]

#         if (x, y) == entry:
#             return ENTRY_T
#         if (x, y) == exit_:
#             return EXIT_T
#         if (x, y) in self.path:
#             return PATH
#         if (x, y) in self.reserved:
#             return RESERVED
#         return PASSAGE

#     def _build_display(self) -> list[list[int]]:
#         h, w = self.maze.height, self.maze.width
#         grid = self.maze.grid
#         rows, cols = 2 * h + 1, 2 * w + 1
#         disp = [[WALL] * cols for _ in range(rows)]
#         path_nodes = {PATH, ENTRY_T, EXIT_T}

#         for y in range(h):
#             for x in range(w):
#                 disp[2 * y + 1][2 * x + 1] = self._cell_type(x, y)

#         for y in range(h):
#             for x in range(w):
#                 cell = grid[y][x]

#                 if x + 1 < w and not (cell & E):
#                     self._set_edge(disp, 2 * y + 1, 2 * (x + 1),
#                                    self._cell_type(x, y), self._cell_type(x + 1, y), path_nodes)

#                 if y + 1 < h and not (cell & S):
#                     self._set_edge(disp, 2 * (y + 1), 2 * x + 1,
#                                    self._cell_type(x, y), self._cell_type(x, y + 1), path_nodes)

#         for y in range(h):
#             for x in range(w):
#                 cell = grid[y][x]
#                 ct = self._cell_type(x, y)

#                 if y == 0 and not (cell & N):
#                     disp[0][2 * x + 1] = ct
#                 if y == h - 1 and not (cell & S):
#                     disp[2 * h][2 * x + 1] = ct
#                 if x == 0 and not (cell & W):
#                     disp[2 * y + 1][0] = ct
#                 if x == w - 1 and not (cell & E):
#                     disp[2 * y + 1][2 * w] = ct

#         self._fix_corners(disp, rows, cols)
#         return disp

#     def _set_edge(
#         self,
#         disp: list[list[int]],
#         dy: int,
#         dx: int,
#         t1: int,
#         t2: int,
#         path_nodes: set[int],
#     ) -> None:
#         if t1 == RESERVED and t2 == RESERVED:
#             disp[dy][dx] = RESERVED
#         elif t1 in path_nodes and t2 in path_nodes:
#             disp[dy][dx] = PATH
#         else:
#             disp[dy][dx] = PASSAGE

#     def _fix_corners(self, disp: list[list[int]], rows: int, cols: int) -> None:
#         for dy in range(rows):
#             for dx in range(cols):
#                 if dy % 2 != 0 or dx % 2 != 0 or disp[dy][dx] != WALL:
#                     continue

#                 adj = []
#                 for ady, adx in ((dy - 1, dx), (dy + 1, dx), (dy, dx - 1), (dy, dx + 1)):
#                     if not (0 <= ady < rows and 0 <= adx < cols) or disp[ady][adx] == WALL:
#                         adj = []
#                         break
#                     adj.append(disp[ady][adx])

#                 if adj:
#                     disp[dy][dx] = RESERVED if all(t == RESERVED for t in adj) else PASSAGE

#     def _init_colors(self) -> None:
#         curses.curs_set(0)
#         curses.start_color()
#         curses.use_default_colors()

#         themes = [
#             (curses.COLOR_WHITE, curses.COLOR_MAGENTA, curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_YELLOW),
#             (curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_WHITE),
#             (curses.COLOR_YELLOW, curses.COLOR_MAGENTA, curses.COLOR_CYAN, curses.COLOR_RED, curses.COLOR_GREEN),
#         ]

#         wall_c, reserved_c, entry_c, exit_c, path_c = themes[self.theme_index % len(themes)]

#         curses.init_pair(1, wall_c, wall_c)
#         curses.init_pair(2, reserved_c, reserved_c)
#         curses.init_pair(3, entry_c, entry_c)
#         curses.init_pair(4, exit_c, exit_c)
#         curses.init_pair(5, path_c, path_c)

#     def _draw_frame(self, stdscr: curses.window) -> int:
#         type_to_pair = {
#             WALL: 1,
#             PASSAGE: 0,
#             RESERVED: 2,
#             ENTRY_T: 3,
#             EXIT_T: 4,
#             PATH: 5,
#         }

#         stdscr.clear()
#         display = self._build_display()

#         for dy, row in enumerate(display):
#             for dx, cell_type in enumerate(row):
#                 try:
#                     stdscr.addstr(dy, dx * 2, "  ", curses.color_pair(type_to_pair.get(cell_type, 0)))
#                 except curses.error:
#                     pass

#         return len(display)

#     def draw(self, stdscr: curses.window) -> None:
#         self._init_colors()
#         rows = self._draw_frame(stdscr)
#         _draw_lines(stdscr, rows + 1, ["Press any key to quit."])
#         stdscr.refresh()
#         stdscr.getch()

#     def animate_path(self, stdscr: curses.window, delay: float = 0.05, show_menu: bool = False) -> int:
#         self._init_colors()
#         full_path = list(self.path)
#         self.path = []

#         rows = 0
#         for cell in full_path:
#             self.path.append(cell)
#             rows = self._draw_frame(stdscr)
#             if show_menu:
#                 _draw_lines(stdscr, rows + 1, MENU_LINES)
#             stdscr.refresh()
#             curses.napms(int(delay * 1000))

#         return rows


# def _draw_lines(stdscr: curses.window, start_y: int, lines: list[str]) -> None:
#     for i, line in enumerate(lines):
#         try:
#             stdscr.addstr(start_y + i, 0, line)
#         except curses.error:
#             pass


# def _draw_display(
#     stdscr: curses.window,
#     maze_gen: "MazeGenerator",
#     path: list[tuple[int, int]] | None,
#     theme_index: int,
#     show_menu: bool = True,
# ) -> int:
#     sd = SimpleDisplay(maze_gen, path or [])
#     sd.theme_index = theme_index
#     sd._init_colors()
#     rows = sd._draw_frame(stdscr)

#     if show_menu:
#         _draw_lines(stdscr, rows + 1, MENU_LINES)

#     stdscr.refresh()
#     return rows


# def _animate_path(
#     stdscr: curses.window,
#     maze_gen: "MazeGenerator",
#     path: list[tuple[int, int]],
#     theme_index: int,
#     show_path: bool = True,
#     delay: float = 0.05,
# ) -> None:
#     sd = SimpleDisplay(maze_gen, path if show_path else [])
#     sd.theme_index = theme_index

#     if show_path:
#         sd.animate_path(stdscr, delay=delay, show_menu=True)
#     else:
#         rows = _draw_display(stdscr, maze_gen, [], theme_index, show_menu=True)
#         stdscr.refresh()


# def _generate_maze(
#     stdscr: curses.window,
#     maze_gen: Any,
#     algo: str,
#     delay: int,
#     theme_index: int,
# ) -> None:
#     if algo == "dfs":
#         maze_gen.dfs_algo(stdscr=stdscr, animate=True, delay=delay, theme_index=theme_index)
#     elif algo == "prim":
#         maze_gen.prim_algo(stdscr=stdscr, animate=True, delay=delay, theme_index=theme_index)
#     else:
#         raise ValueError("algo must be 'dfs' or 'prim'")


# def _regenerate_maze(maze_gen: Any, algo: str) -> Any:
#     new_gen = type(maze_gen)(maze_gen.config)

#     if hasattr(maze_gen, "reserved"):
#         try:
#             new_gen.set_42()
#         except Exception:
#             pass

#     return new_gen


# def render_maze(maze_gen: "MazeGenerator", path: list[tuple[int, int]]) -> None:
#     curses.wrapper(SimpleDisplay(maze_gen, path).draw)


# def animate_maze(maze_gen: "MazeGenerator", path: list[tuple[int, int]], delay: float = 0.08) -> None:
#     curses.wrapper(lambda stdscr: SimpleDisplay(maze_gen, path).animate_path(stdscr, delay=delay, show_menu=False))


# def draw_generation_frame(stdscr: curses.window, maze_gen: "MazeGenerator", theme_index: int = 0) -> None:
#     _draw_display(stdscr, maze_gen, [], theme_index, show_menu=False)


# def animate_generation(maze_gen: "MazeGenerator", algo: str = "dfs", delay: int = 20) -> None:
#     curses.wrapper(lambda stdscr: _run_generation(stdscr, maze_gen, algo, delay))


# def _run_generation(stdscr: curses.window, maze_gen: Any, algo: str, delay: int) -> None:
#     curses.curs_set(0)
#     _generate_maze(stdscr, maze_gen, algo, delay, theme_index=0)
#     rows = _draw_display(stdscr, maze_gen, [], theme_index=0, show_menu=True)
#     stdscr.getch()


# def simple_menu_maze(maze_gen, path, algo="dfs", gen_delay=15):
#     curses.wrapper(lambda stdscr: _simple_menu_loop(stdscr, maze_gen, path, algo, gen_delay))


# def _simple_menu_loop(stdscr, maze_gen, path, algo, gen_delay):
#     curses.curs_set(0)

#     full_path = path
#     show_path = True
#     theme_index = 0

#     _animate_path(stdscr, maze_gen, full_path, theme_index, show_path)

#     while True:
#         current_path = full_path if show_path else []
#         _draw_display(stdscr, maze_gen, current_path, theme_index, show_menu=True)
#         key = stdscr.getch()

#         if key == ord("1"):
#             maze_gen = _regenerate_maze(maze_gen, algo)
#             _generate_maze(stdscr, maze_gen, algo, gen_delay, theme_index)
#             full_path = maze_gen.solve_bfs(maze_gen.config["ENTRY"], maze_gen.config["EXIT"])
#             _animate_path(stdscr, maze_gen, full_path, theme_index, show_path)

#         elif key == ord("2"):
#             show_path = not show_path

#         elif key == ord("3"):
#             theme_index += 1

#         elif key == ord("4"):
#             break