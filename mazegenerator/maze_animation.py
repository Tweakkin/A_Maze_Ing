import curses
from typing import TYPE_CHECKING, Optional

from mazegenerator.display_maze import draw_generation_frame

if TYPE_CHECKING:
    from mazegenerator import MazeGenerator


def animate_step(
    stdscr: Optional[curses.window],
    maze_gen: 'MazeGenerator',
    delay: int = 20,
    theme_index: int = 0,
) -> None:
    # Redraw the maze state for one animation step, then pause briefly.
    if stdscr is not None:
        draw_generation_frame(stdscr, maze_gen, theme_index)
        curses.napms(delay)
