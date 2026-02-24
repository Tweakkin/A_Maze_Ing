import curses
import time
from collections import deque

# ─────────────────────────────────────────────────────────────────
#  WALL CONSTANTS
# ─────────────────────────────────────────────────────────────────
NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

DELTA = {
    NORTH: (0, -1),
    SOUTH: (0,  1),
    EAST:  (1,  0),
    WEST:  (-1, 0),
}

# ─────────────────────────────────────────────────────────────────
#  COLOR PAIR IDs
# ─────────────────────────────────────────────────────────────────
C_WALL    = 1   # blue background  → walls and borders
C_FLOOR   = 2   # default bg       → empty cell
C_ENTRY   = 3   # green            → start cell  'S'
C_EXIT    = 4   # red              → end cell    'E'
C_PATH    = 5   # yellow           → solution path
C_VISITED = 6   # cyan             → BFS explored cells
C_TITLE   = 7   # white on blue    → title bar


# ═════════════════════════════════════════════════════════════════
class MazeDisplay:
    """
    Curses-based interactive display for the maze.

    Usage
    -----
        display = MazeDisplay(gen.grid, width, height, entry, exit_)
        curses.wrapper(display.draw)

    Parameters
    ----------
    grid   : list[list[int]]  — gen.grid, grid[y][x] = wall bitmask
    width  : int              — number of columns
    height : int              — number of rows
    entry  : (x, y)           — start cell coordinates
    exit_  : (x, y)           — end cell coordinates
    """

    def __init__(self, grid, width, height, entry, exit_):
        self.grid   = grid
        self.width  = width
        self.height = height
        self.entry  = entry
        self.exit_  = exit_

        # State
        self.solution = set()   # (x,y) cells on the solution path
        self.visited  = set()   # (x,y) cells explored by BFS
        self.info_msg = 'Maze ready.  Use the keys below.'

    # ──────────────────────────────────────────────────────────────
    #  ENTRY POINT  — called by curses.wrapper(display.draw)
    # ──────────────────────────────────────────────────────────────

    def draw(self, stdscr):
        self._setup_colors()
        curses.curs_set(0)      # hide cursor
        stdscr.keypad(True)     # enable arrow keys / special keys

        self.stdscr = stdscr
        self._compute_offsets()
        self._full_redraw()

        # ── Keyboard event loop ───────────────────────────────────
        while True:
            key = stdscr.getch()

            if key in (ord('q'), ord('Q')):
                # Quit
                break

            elif key in (ord('r'), ord('R')):
                # Reset — clear solution and visited
                self.solution.clear()
                self.visited.clear()
                self.info_msg = 'Reset.  Maze ready.'
                self._full_redraw()

            elif key in (ord('s'), ord('S')):
                # Instant solve
                path, vis     = self._bfs_solve()
                self.solution = set(path)
                self.visited  = vis
                self.info_msg = (
                    f'Solved!  Path length: {len(path)} steps.'
                    if path else 'No solution found.'
                )
                self._full_redraw()

            elif key in (ord('a'), ord('A')):
                # Animated BFS solve
                self.solution.clear()
                self.visited.clear()
                sol, vis      = self._animate_solve()
                self.solution = sol
                self.visited  = vis
                self.info_msg = (
                    f'Done!  Path length: {len(sol)} steps.'
                    if sol else 'No solution found.'
                )
                self._draw_hud()
                stdscr.refresh()

    # ──────────────────────────────────────────────────────────────
    #  LAYOUT HELPERS
    # ──────────────────────────────────────────────────────────────

    def _compute_offsets(self):
        """Calculate where to place the maze so it is centered."""
        max_rows, max_cols = self.stdscr.getmaxyx()

        # Maze needs (height*2 + 1) rows and (width*2 + 1) cols
        maze_rows = self.height * 2 + 1
        maze_cols = self.width  * 2 + 1

        # Leave 2 rows above for the title, 4 rows below for the HUD
        self.offset_row = max(2, (max_rows - maze_rows - 4) // 2)
        self.offset_col = max(1, (max_cols - maze_cols)     // 2)

        self.hud_row = self.offset_row + maze_rows + 1

    # ──────────────────────────────────────────────────────────────
    #  FULL REDRAW
    # ──────────────────────────────────────────────────────────────

    def _full_redraw(self):
        self.stdscr.clear()
        self._draw_title()
        self._draw_maze()
        self._draw_hud()
        self.stdscr.refresh()

    # ──────────────────────────────────────────────────────────────
    #  TITLE
    # ──────────────────────────────────────────────────────────────

    def _draw_title(self):
        title = '  A_MAZE_ING — Interactive Maze  '
        self._safe_addstr(
            self.offset_row - 2, self.offset_col,
            title,
            curses.A_BOLD | curses.color_pair(C_TITLE)
        )

    # ──────────────────────────────────────────────────────────────
    #  MAZE DRAWING
    # ──────────────────────────────────────────────────────────────

    def _draw_maze(self):
        """
        Draw every cell, wall, and border of the maze.

        Screen layout for cell (cx, cy):
          row = offset_row + cy*2 + 1   → interior row
          col = offset_col + cx*2       → left edge of cell
        """
        wall  = curses.color_pair(C_WALL)
        floor = curses.color_pair(C_FLOOR)
        or_   = self.offset_row
        oc    = self.offset_col

        # ── Top border ────────────────────────────────────────────
        for cx in range(self.width):
            c = oc + cx * 2
            self._safe_addch(or_, c,     '+', wall)
            self._safe_addch(or_, c + 1, '-', wall)
        self._safe_addch(or_, oc + self.width * 2, '+', wall)

        # ── Row by row ────────────────────────────────────────────
        for cy in range(self.height):
            r_int = or_ + cy * 2 + 1   # interior row
            r_bot = or_ + cy * 2 + 2   # bottom border row

            for cx in range(self.width):
                c          = oc + cx * 2
                cell_attr, cell_ch = self._cell_appearance(cx, cy)

                # West wall
                if self.grid[cy][cx] & WEST:
                    self._safe_addch(r_int, c, '|', wall)
                else:
                    self._safe_addch(r_int, c, ' ', cell_attr)

                # Interior character
                self._safe_addch(r_int, c + 1, cell_ch, cell_attr)

            # East border of the row
            self._safe_addch(r_int, oc + self.width * 2, '|', wall)

            # Bottom border of this row
            for cx in range(self.width):
                c = oc + cx * 2
                self._safe_addch(r_bot, c, '+', wall)
                if self.grid[cy][cx] & SOUTH:
                    self._safe_addch(r_bot, c + 1, '-', wall)
                else:
                    self._safe_addch(r_bot, c + 1, ' ', floor)
            self._safe_addch(r_bot, oc + self.width * 2, '+', wall)

    def _cell_appearance(self, cx, cy):
        """Return (color_attr, character) for a cell's interior."""
        pos = (cx, cy)
        if pos == self.entry:
            return curses.color_pair(C_ENTRY),   'S'
        if pos == self.exit_:
            return curses.color_pair(C_EXIT),    'E'
        if pos in self.solution:
            return curses.color_pair(C_PATH),    '\xb7'  # · middle dot
        if pos in self.visited:
            return curses.color_pair(C_VISITED), ' '
        return curses.color_pair(C_FLOOR), ' '

    # ──────────────────────────────────────────────────────────────
    #  HUD  (info + legend + controls)
    # ──────────────────────────────────────────────────────────────

    def _draw_hud(self):
        r = self.hud_row
        c = self.offset_col

        # Info message line
        self._safe_addstr(r, c,
                          self.info_msg.ljust(70),
                          curses.A_BOLD)

        # Legend line
        legend = [
            (C_ENTRY,   'S', 'Start'),
            (C_EXIT,    'E', 'End'),
            (C_PATH,    '\xb7', 'Path'),
            (C_VISITED, ' ', 'Visited'),
        ]
        lc = c
        self._safe_addstr(r + 1, lc, 'Legend: ', curses.A_BOLD)
        lc += 8
        for pair_id, ch, label in legend:
            self._safe_addch(r + 1,  lc,     ch,
                             curses.color_pair(pair_id))
            self._safe_addstr(r + 1, lc + 1, f' {label}   ')
            lc += len(label) + 4

        # Controls line
        self._safe_addstr(
            r + 2, c,
            '[S] Solve   [A] Animate   [R] Reset   [Q] Quit',
            curses.A_DIM
        )

    # ──────────────────────────────────────────────────────────────
    #  BFS SOLVER  (instant)
    # ──────────────────────────────────────────────────────────────

    def _bfs_solve(self):
        """
        BFS from entry to exit.
        Returns (path, visited_set).
        path is a list of (x,y) — empty if no solution.
        """
        parent  = {self.entry: None}
        queue   = deque([self.entry])
        visited = set()

        while queue:
            x, y = queue.popleft()
            visited.add((x, y))

            if (x, y) == self.exit_:
                path, node = [], self.exit_
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path, visited

            for direction, (dx, dy) in DELTA.items():
                nx, ny = x + dx, y + dy
                if (self._in_bounds(nx, ny)
                        and (nx, ny) not in parent
                        and not (self.grid[y][x] & direction)):
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        return [], visited

    # ──────────────────────────────────────────────────────────────
    #  ANIMATED BFS SOLVE
    # ──────────────────────────────────────────────────────────────

    def _animate_solve(self, speed=0.03):
        """
        BFS with a redraw after every step so the user watches it
        explore the maze in real time.
        Returns (solution_set, visited_set).
        """
        parent  = {self.entry: None}
        queue   = deque([self.entry])
        visited = set()
        found   = False

        while queue and not found:
            x, y = queue.popleft()
            visited.add((x, y))

            # Partial redraw — update maze + info only (faster than full clear)
            self.visited  = visited
            self.info_msg = f'Searching...  cells visited: {len(visited)}'
            self.stdscr.clear()
            self._draw_title()
            self._draw_maze()
            self._draw_hud()
            self.stdscr.refresh()
            time.sleep(speed)

            if (x, y) == self.exit_:
                found = True
                break

            for direction, (dx, dy) in DELTA.items():
                nx, ny = x + dx, y + dy
                if (self._in_bounds(nx, ny)
                        and (nx, ny) not in parent
                        and not (self.grid[y][x] & direction)):
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        if not found:
            return set(), visited

        # Reconstruct path
        path, node = [], self.exit_
        while node is not None:
            path.append(node)
            node = parent[node]
        path.reverse()

        # Animate the path highlight step by step
        solution = set()
        for step in path:
            solution.add(step)
            self.solution = solution
            self.stdscr.clear()
            self._draw_title()
            self._draw_maze()
            self._draw_hud()
            self.stdscr.refresh()
            time.sleep(0.06)

        return solution, visited

    # ──────────────────────────────────────────────────────────────
    #  UTILITIES
    # ──────────────────────────────────────────────────────────────

    def _in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def _safe_addch(self, row, col, ch, attr=0):
        """addch that never crashes on screen-edge writes."""
        try:
            self.stdscr.addch(row, col, ch, attr)
        except curses.error:
            pass

    def _safe_addstr(self, row, col, text, attr=0):
        try:
            self.stdscr.addstr(row, col, text, attr)
        except curses.error:
            pass

    # ──────────────────────────────────────────────────────────────
    #  COLOR SETUP
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _setup_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(C_WALL,    curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(C_FLOOR,   curses.COLOR_WHITE, -1)
        curses.init_pair(C_ENTRY,   curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(C_EXIT,    curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(C_PATH,    curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(C_VISITED, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(C_TITLE,   curses.COLOR_WHITE, curses.COLOR_BLUE)
