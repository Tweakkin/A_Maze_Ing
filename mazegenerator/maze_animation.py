import curses
from mazegenerator.display_maze import SimpleDisplay, draw_generation_frame


def animate_step(stdscr, maze_gen, delay=20, theme_index=0):
    if stdscr is not None:
        draw_generation_frame(stdscr, maze_gen, theme_index)
        curses.napms(delay)
		