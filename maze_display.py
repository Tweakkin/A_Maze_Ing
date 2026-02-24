import curses
import time

class MazeDisplay:
    # Constants dyal l-ittijahat (khass y-kouno n-fshom 3and sa7bak)
    N, E, S, W = 1, 2, 4, 8

    def __init__(self, grid):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])

    def draw(self, stdscr):
        # 1. I3dadat l-affichages
        curses.curs_set(0) # Khbi l-curseur
        stdscr.clear()

        # 2. Boucle bash n-rsmou kol cell
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                
                # 7seb l-makan f-l-terminal
                sy, sx = y * 2, x * 4

                # Rsem l-qant (Corner)
                stdscr.addstr(sy, sx, "+")

                # --- Rsem l-7it dyal l-North ---
                if cell & self.N:
                    stdscr.addstr(sy, sx + 1, "---")
                else:
                    stdscr.addstr(sy, sx + 1, "   ")

                # --- Rsem l-7it dyal l-West ---
                if cell & self.W:
                    stdscr.addstr(sy + 1, sx, "|")
                else:
                    stdscr.addstr(sy + 1, sx, " ")

                # --- Rsem l-7it dyal l-East (ghir l-l-cells li f-l-liman bzaf) ---
                if x == self.width - 1:
                    if cell & self.E:
                        stdscr.addstr(sy, sx + 4, "+")
                        stdscr.addstr(sy + 1, sx + 4, "|")
                    else:
                        stdscr.addstr(sy, sx + 4, "+")

                # --- Rsem l-7it dyal l-South (ghir l-l-cells li f-l-te7t bzaf) ---
                if y == self.height - 1:
                    if cell & self.S:
                        stdscr.addstr(sy + 2, sx, "+---")
                        if x == self.width - 1:
                            stdscr.addstr(sy + 2, sx + 4, "+")
                    else:
                        stdscr.addstr(sy + 2, sx, "+   ")

        stdscr.refresh()
        stdscr.getch() # Tsanna l-user y-cliki 3la chi 7aja bash y-khrej

# --- Kifach ghadi t-khdemha f-l-main ---
def main():
    # Mital dyal grid (3x3) ga3 l-7youta m-s-doudin (15)
    # Had l-grid ghadi t-koun jaya men l-code dyal sa7bak
    sample_grid = [[15, 15, 15], [15, 15, 15], [15, 15, 15]]
    
    display = MazeDisplay(sample_grid)
    
    # Khdem curses b-stikhdam l-wrapper bash t-koun safe
    curses.wrapper(display.draw)

if __name__ == "__main__":
    main()