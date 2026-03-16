import sys
import random
from mazegenerator.config_parser import ConfigPasrer
from mazegenerator.mazegenerator import MazeGenerator
from mazegenerator.display_maze import animate_generation, simple_menu_maze
from mazegenerator.primalgo import PrimGenerator
# after

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
        algo = toparse.parsed_dict['ALGO']
        gen_class = MazeGenerator if algo == "dfs" else PrimGenerator
        gen = gen_class(toparse.parsed_dict)
        gen.set_42()
        if toparse.parsed_dict['ENTRY'] in gen.reserved:
            print(
                f"Error: ENTRY {toparse.parsed_dict['ENTRY']}"
                " overlaps with the '42' pattern.")
            sys.exit(0)
        if toparse.parsed_dict['EXIT'] in gen.reserved:
            print(
                f"Error: EXIT {toparse.parsed_dict['EXIT']}"
                " overlaps with the '42' pattern.")
            sys.exit(0)
        animate_generation(gen, algo=algo, delay=15)
        path = gen.solve_bfs(
            toparse.parsed_dict['ENTRY'], toparse.parsed_dict['EXIT'])
        if not path:
            print("Error: No path found between ENTRY and EXIT.")
            sys.exit(0)
        gen.write_to_file(toparse.parsed_dict['OUTPUT_FILE'], path)
        simple_menu_maze(gen, path, algo=algo)
        return

    except Exception as e:
        print(e)
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("CTRL C")
        sys.exit(0)
