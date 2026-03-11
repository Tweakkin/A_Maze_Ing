import sys
import random
from config_parser import ConfigPasrer
from mazegenerator import MazeGenerator
from display_maze import render_maze, animate_maze, animate_generation, simple_menu_maze
from primalgo import PrimGenerator

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

def main():
    if len(sys.argv) != 2:
        print("Error: Usage is python3 a_maze_ing.py <config_file>")
        sys.exit(0)

    toparse = ConfigPasrer(sys.argv[1])
    toparse.parse()
    
    if toparse.parsed_dict['SEED'] is not None:
        random.seed(toparse.parsed_dict['SEED'])

    try:
        gen = MazeGenerator(toparse.parsed_dict)
        gen.set_42()
        if toparse.parsed_dict['ENTRY'] in gen.reserved:
            print(f"Error: ENTRY {toparse.parsed_dict['ENTRY']} overlaps with the '42' pattern.")
            sys.exit(0)
        if toparse.parsed_dict['EXIT'] in gen.reserved:
            print(f"Error: EXIT {toparse.parsed_dict['EXIT']} overlaps with the '42' pattern.")
            sys.exit(0)
        animate_generation(gen, algo="dfs", delay=15)
        #gen.set_entry_exit()
        # gen.dfs_algo()
        path = gen.solve_bfs(toparse.parsed_dict['ENTRY'], toparse.parsed_dict['EXIT'])
        if not path:
            print("Error: No path found between ENTRY and EXIT.")
            sys.exit(0)
        simple_menu_maze(gen, path, algo="dfs")


        gen2 = PrimGenerator(toparse.parsed_dict)
        gen2.set_42()
        if toparse.parsed_dict['ENTRY'] in gen2.reserved:
            print(f"Error: ENTRY {toparse.parsed_dict['ENTRY']} overlaps with the '42' pattern.")
            sys.exit(0)
        if toparse.parsed_dict['EXIT'] in gen2.reserved:
            print(f"Error: EXIT {toparse.parsed_dict['EXIT']} overlaps with the '42' pattern.")
            sys.exit(0)
        animate_generation(gen2, algo="prim", delay=15)
        # gen2.prim_algo()
        path = gen2.solve_bfs(toparse.parsed_dict['ENTRY'], toparse.parsed_dict['EXIT'])
        if not path:
            print("Error: No path found between ENTRY and EXIT.")
            sys.exit(0)
        gen2.write_to_file(toparse.parsed_dict['OUTPUT_FILE'], path)
        animate_maze(gen2, path, delay=0.08)

    except Exception as e:
        print(e)
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(f"CTRL C")
        sys.exit(0)


    # sys.argv must contain exactly 2 items: [script_name, config_file]
   