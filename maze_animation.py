import curses
from display_maze import SimpleDisplay


def draw_generation_frame(stdscr, maze_gen):
    sd = SimpleDisplay(maze_gen, path=[])
    sd._init_colors()
    sd._draw_frame(stdscr)
    stdscr.refresh()


def animate_step(stdscr, maze_gen, delay=20):
    if stdscr is not None:
        draw_generation_frame(stdscr, maze_gen)
        curses.napms(delay)


def animate_generation(maze_gen, algo="dfs", delay=20):
    curses.wrapper(lambda stdscr: _run_generation(stdscr, maze_gen, algo, delay))


def _run_generation(stdscr, maze_gen, algo, delay):
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