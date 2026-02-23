import curses
from curses import wrapper


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

def to_display(stdscr, maze):
	curses.start_color()
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
	curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	width = maze.width
	height = maze.height
	max_y, max_x = stdscr.getmaxyx()
	for y in range(height):
		for x in range(width):
			row = y * 2
			col = x * 4
			if row < max_y - 1 and col < max_x - 2:
				stdscr.addstr(row, col, " ", curses.color_pair(2))
				if maze.has_wall(x, y, NORTH):
					stdscr.addstr(row, col + 1, "  ", curses.color_pair(2))
				else:
					stdscr.addstr(row, col + 1, "  ", curses.color_pair(0))
				if maze.has_wall(x, y, WEST):
					stdscr.addstr(row + 1, col, " ", curses.color_pair(2))
				else:
					stdscr.addstr(row + 1, col, " ", curses.color_pair(0))
				stdscr.addstr(row + 1, col + 1, "   ", curses.color_pair(0))
	for y in range(height):
		row = y * 2
		col = width * 4
		stdscr.addstr(row, col, " ", curses.color_pair(2))
		if maze.has_wall(width - 1, y, EAST):
			stdscr.addstr(row + 1, col, " ", curses.color_pair(2))
	
	for x in range(width):
		row = height * 2
		col = x * 4
		stdscr.addstr(row, col, " ", curses.color_pair(2))
		if maze.has_wall(x, height - 1, SOUTH):
			stdscr.addstr(row, col + 1, " ", curses.color_pair(2))

	stdscr.addstr(height * 2, width * 4, " ", curses.color_pair(2))


	stdscr.refresh()
	stdscr.getch()