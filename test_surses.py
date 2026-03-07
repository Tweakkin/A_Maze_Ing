import curses

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(5, 10, "Curses is working")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)