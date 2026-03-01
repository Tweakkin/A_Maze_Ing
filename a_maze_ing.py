import sys
from config_parser import ConfigPasrer
from mazegenerator import MazeGenerator
from display_maze import render_maze
from primalgo import PrimGenerator

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
        gen.set_42()
        gen.dfs_algo()
        path = gen.solve_bfs(toparse.parsed_dict['ENTRY'], toparse.parsed_dict['EXIT'])
        render_maze(gen, path)


        gen2 = PrimGenerator(toparse.parsed_dict)
        gen2.set_42()
        gen2.prim_algo()
        path = gen2.solve_bfs(toparse.parsed_dict['ENTRY'], toparse.parsed_dict['EXIT'])
        render_maze(gen2, path)

    except Exception as e:
        print(e)
        sys.exit(1)