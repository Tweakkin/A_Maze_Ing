import sys
from config_parser import ConfigPasrer

class MazeGenerator:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        self.grid = []
        for _ in range(height):
            temp = []
            for _ in range(width):
                temp.append(15)
            self.grid.append(temp)
    
    def get_cell(self, x:int, y:int) -> int:
        return self.grid[x][y]

    

if __name__ == "__main__":

    # sys.argv must contain exactly 2 items: [script_name, config_file]
    if len(sys.argv) != 2:
        print("Error: Usage is python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    
    toparse = ConfigPasrer(sys.argv[1])
    toparse.parse()
    
    gen = MazeGenerator(toparse.parsed_dict['WIDTH'], toparse.parsed_dict['HEIGHT'])
    
    a = 15
    print(5 & 2)