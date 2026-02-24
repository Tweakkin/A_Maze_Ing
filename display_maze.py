import curses
from collections import deque

N, E, S, W = 1, 2, 4, 8
DIRECTIONS = {N: (0, -1), S: (0, 1), E: (1, 0), W: (-1, 0)}

# Display cell types
WALL = 0
PASSAGE = 1
RESERVED = 2
ENTRY_T = 3
EXIT_T = 4
PATH = 5


class MazeDisplay:

    def __init__(self, maze_gen):
        self.maze = maze_gen
        self.show_path = False
        self.path_cells = set()
        self.color_scheme = 0
        self.num_schemes = 4
        self._solve()

    def _solve(self):
        """BFS from entry to exit to find the solution path."""
        grid = self.maze.grid
        h, w = self.maze.height, self.maze.width
        entry = self.maze.config['ENTRY']
        exit_pos = self.maze.config['EXIT']

        queue = deque([(entry, [entry])])
        visited = {entry}

        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == exit_pos:
                self.path_cells = set(path)
                return
            for d, (dx, dy) in DIRECTIONS.items():
                if not (grid[cy][cx] & d):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [(nx, ny)]))
        self.path_cells = set()

    def _cell_type(self, x, y):
        """Return the display type for maze cell (x, y)."""
        if (x, y) == self.maze.config['ENTRY']:
            return ENTRY_T
        if (x, y) == self.maze.config['EXIT']:
            return EXIT_T
        if (x, y) in getattr(self.maze, 'reserved', set()):
            return RESERVED
        if self.show_path and (x, y) in self.path_cells:
            return PATH
        return PASSAGE

    def _edge_type(self, t1, t2):
        """Determine display type for an edge between two cells."""
        if t1 == RESERVED and t2 == RESERVED:
            return RESERVED
        if t1 in (PATH, ENTRY_T, EXIT_T) and t2 in (PATH, ENTRY_T, EXIT_T):
            return PATH
        return PASSAGE

    def _build_display(self):
        """Build a (2H+1) x (2W+1) grid where each position has a display type.

        Even rows/cols = walls or corners, odd rows/cols = cell interiors.
        Each position is tagged: WALL, PASSAGE, RESERVED, ENTRY_T, EXIT_T, PATH.
        """
        h = self.maze.height
        w = self.maze.width
        grid = self.maze.grid
        rows = 2 * h + 1
        cols = 2 * w + 1

        disp = [[WALL] * cols for _ in range(rows)]

        # 1) Cell interiors (odd row, odd col)
        for y in range(h):
            for x in range(w):
                disp[2 * y + 1][2 * x + 1] = self._cell_type(x, y)

        # 2) Internal edges (passages between adjacent cells)
        for y in range(h):
            for x in range(w):
                cell = grid[y][x]
                # East edge
                if x + 1 < w and not (cell & E):
                    t1 = self._cell_type(x, y)
                    t2 = self._cell_type(x + 1, y)
                    disp[2 * y + 1][2 * (x + 1)] = self._edge_type(t1, t2)
                # South edge
                if y + 1 < h and not (cell & S):
                    t1 = self._cell_type(x, y)
                    t2 = self._cell_type(x, y + 1)
                    disp[2 * (y + 1)][2 * x + 1] = self._edge_type(t1, t2)

        # 3) Border openings (entry / exit holes in the outer wall)
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

        # 4) Fix corners: remove wall at corners surrounded entirely by non-walls
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
                        elif any(t == PATH for t in adj_types):
                            disp[dy][dx] = PATH
                        else:
                            disp[dy][dx] = PASSAGE

        return disp

    def _init_colors(self, scheme):
        """Set up curses color pairs for the given color scheme."""
        curses.start_color()
        curses.use_default_colors()

        # Determine gray for 42 cells
        if curses.COLORS >= 256:
            gray = 245
        elif curses.can_change_color():
            curses.init_color(8, 500, 500, 500)
            gray = 8
        else:
            gray = curses.COLOR_WHITE

        wall_colors = [
            curses.COLOR_WHITE,
            curses.COLOR_GREEN,
            curses.COLOR_BLUE,
            curses.COLOR_CYAN,
        ]
        wc = wall_colors[scheme % len(wall_colors)]

        curses.init_pair(1, wc, wc)                                          # walls
        curses.init_pair(2, gray, gray)                                      # 42
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)      # entry
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)              # exit
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLUE)            # path

    def _regenerate(self):
        """Reset grid and regenerate a new maze."""
        h = self.maze.height
        w = self.maze.width
        self.maze.grid = [[15] * w for _ in range(h)]
        self.maze.set_42()
        self.maze.dfs_algo()
        self.maze.set_entry_exit()
        self._solve()

    def draw(self, stdscr):
        """Main curses draw loop with interactive menu."""
        curses.curs_set(0)
        self._init_colors(self.color_scheme)

        type_to_pair = {
            WALL: 1,
            PASSAGE: 0,
            RESERVED: 2,
            ENTRY_T: 3,
            EXIT_T: 4,
            PATH: 5,
        }

        while True:
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

            # Menu
            menu_y = rows + 1
            try:
                stdscr.addstr(menu_y, 0, "=== A-Maze-Ing ===", curses.A_BOLD)
                stdscr.addstr(menu_y + 1, 0, "1. Re-generate a new maze")
                stdscr.addstr(menu_y + 2, 0, "2. Show/Hide path from entry to exit")
                stdscr.addstr(menu_y + 3, 0, "3. Rotate maze colors")
                stdscr.addstr(menu_y + 4, 0, "4. Quit")
                stdscr.addstr(menu_y + 5, 0, "Choice? (1-4): ")
            except curses.error:
                pass

            stdscr.refresh()
            key = stdscr.getch()

            if key == ord('1'):
                self._regenerate()
            elif key == ord('2'):
                self.show_path = not self.show_path
            elif key == ord('3'):
                self.color_scheme = (self.color_scheme + 1) % self.num_schemes
                self._init_colors(self.color_scheme)
            elif key == ord('4'):
                break


def display_maze(maze_gen):
    """Entry point — launch curses display for the given MazeGenerator."""
    md = MazeDisplay(maze_gen)
    curses.wrapper(md.draw)
