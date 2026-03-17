import sys
import random
from mazegenerator.config_parser import ConfigPasrer
from mazegenerator.mazegenerator import MazeGenerator
from mazegenerator.display_maze import animate_generation, simple_menu_maze
from mazegenerator.primalgo import PrimGenerator

# Direction constants
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


# Entry point: parses config, generates maze, solves, displays, and exports
def main() -> None:
    # Validate command-line arguments
    if len(sys.argv) != 2:
        print("Error: Usage is python3 a_maze_ing.py <config_file>")
        sys.exit(0)

    # Parse and validate the config file
    toparse = ConfigPasrer(sys.argv[1])
    toparse.parse()

    # Set the random seed if provided
    if toparse.parsed_dict['SEED'] is not None:
        random.seed(toparse.parsed_dict['SEED'])

    try:
        # Choose generator class based on ALGO config
        algo = toparse.parsed_dict['ALGO']
        gen_class = MazeGenerator if algo == "dfs" else PrimGenerator
        gen = gen_class(toparse.parsed_dict)
        # Embed the "42" pattern into the maze
        gen.set_42()
        # Check that ENTRY does not overlap with the "42" pattern
        if toparse.parsed_dict['ENTRY'] in gen.reserved:
            print(
                f"Error: ENTRY {toparse.parsed_dict['ENTRY']}"
                " overlaps with the '42' pattern.")
            sys.exit(0)
        # Check that EXIT does not overlap with the "42" pattern
        if toparse.parsed_dict['EXIT'] in gen.reserved:
            print(
                f"Error: EXIT {toparse.parsed_dict['EXIT']}"
                " overlaps with the '42' pattern.")
            sys.exit(0)
        # Animate maze generation in the terminal
        animate_generation(gen, algo=algo, delay=15)
        # Solve the maze using BFS
        path = gen.solve_bfs(
            toparse.parsed_dict['ENTRY'], toparse.parsed_dict['EXIT'])
        if not path:
            print("Error: No path found between ENTRY and EXIT.")
            sys.exit(0)
        # Write maze and solution to output file
        gen.write_to_file(toparse.parsed_dict['OUTPUT_FILE'], path)
        # Launch the interactive menu
        simple_menu_maze(gen, path, algo=algo)
        return

    except Exception as e:
        print(e)
        sys.exit(0)


# Run main and handle keyboard interrupt
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("CTRL C")
        sys.exit(0)
