import sys
import curses
from config_parser import ConfigPasrer
from mazegenerator import MazeGenerator
from maze_display  import MazeDisplay

NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

if __name__ == "__main__":

    # ── 1. Check command-line arguments ──────────────────────────────
    if len(sys.argv) != 2:
        print("Error: Usage is python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    # ── 2. Parse config file ──────────────────────────────────────────
    toparse = ConfigPasrer(sys.argv[1])
    toparse.parse()

    # ── 3. Validate required keys exist ──────────────────────────────
    required = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'PERFECT']
    for key in required:
        if key not in toparse.parsed_dict:
            print(f"Error: Missing required config key: {key}")
            sys.exit(1)

    # ── 4. Extract config values ──────────────────────────────────────
    try:
        width   = toparse.parsed_dict['WIDTH']
        height  = toparse.parsed_dict['HEIGHT']
        entry   = toparse.parsed_dict['ENTRY']   # expected: (x, y) tuple
        exit_   = toparse.parsed_dict['EXIT']     # expected: (x, y) tuple
        perfect = toparse.parsed_dict['PERFECT']  # expected: bool
    except Exception as e:
        print(f"Error: Invalid config value — {e}")
        sys.exit(1)

    # ── 5. Generate the maze ──────────────────────────────────────────
    try:
        gen = MazeGenerator(width, height)
        gen.dfs_algo()

        if not perfect:
            total_loops = int(width * height * 0.1)
            gen.make_imperfect(total_loops)

    except Exception as e:
        print(f"Error during maze generation: {e}")
        sys.exit(1)

    # ── 6. Launch curses display ──────────────────────────────────────
    try:
        display = MazeDisplay(gen.grid, width, height, entry, exit_)
        curses.wrapper(display.draw)

    except Exception as e:
        print(f"Error during display: {e}")
        sys.exit(1)