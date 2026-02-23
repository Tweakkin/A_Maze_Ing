import sys
from display import to_display
from config_parser import ConfigPasrer
from mazegenerator import MazeGenerator
from curses import wrapper

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

if __name__ == "__main__":

    # sys.argv must contain exactly 2 items: [script_name, config_file]
    if len(sys.argv) != 2:
        print("Error: Usage is python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    
    toparse = ConfigPasrer(sys.argv[1])
    toparse.parse()
    
    try:
        gen = MazeGenerator(toparse.parsed_dict)
        
        gen.print_grid()
        print("CLOSED MAZE")
        gen.display()
        print()
        gen.dfs_algo()
        gen.print_grid()
        print("AFTER DFS")
        gen.display()

        if toparse.parsed_dict['PERFECT'] == False:
            tot = (toparse.parsed_dict['HEIGHT'] * toparse.parsed_dict['WIDTH']) * 0.1
            gen.make_imperfect(tot)
            print("IMPERFECT MAZE")
            gen.display()
        print()
        gen.set_entry_exit()
        print("ENTRY AND EXIT ACTIVATION")
        gen.display()
        wrapper(to_display, gen)
    except Exception as e:
        print(e)
        sys.exit(1)