import random

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

OPPOSITE = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST
}

DIRECTION_D = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    EAST: (1, 0),
    WEST: (-1, 0)
}

class MazeGenerator:

    def __init__(self, width: int, height: int) -> None:
        if not isinstance(width, int) or width <= 0:
            raise ValueError('width must be a positive integer!')
        if not isinstance(height, int) or height <= 0:
            raise ValueError('height must be a positive integer!')
        self.width = width
        self.height = height

        self.grid = []
        for _ in range(height):
            temp = []
            for _ in range(width):
                temp.append(15)
            self.grid.append(temp)
    
    def get_cell(self, x:int, y:int) -> int:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Cell ({x}, {y}) is out of bounds for {self.width}x{self.height} grid.")
        return self.grid[y][x]
    
    def has_wall(self, x:int, y:int, wall_bit: int) -> bool:
        if wall_bit not in DIRECTION_D:
            raise ValueError(f"Invalid wall bit: {wall_bit}")

        if not(0 <= x < self.width and 0 <= y < self.height):
            return False
        
        return (self.grid[y][x] & wall_bit) != 0
    
    def remove_wall(self, x: int, y: int, direction) -> None:

        if direction not in DIRECTION_D:
            raise ValueError(f"Invalid direction: {direction}, Use NORTH, SOUTH, EAST or WEST.")
        
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        self.grid[y][x] = self.grid[y][x] & ~direction

        dx, dy = DIRECTION_D[direction]
        nx = x + dx
        ny = y + dy
        if 0 <= nx < self.width and 0 <= ny < self.height:
            self.grid[ny][nx] = self.grid[ny][nx] & ~OPPOSITE[direction]

    def print_grid(self) -> None:
        print(self.grid)
    
    def get_neighbors(self, x:int, y:int) -> list:
        neighbors = []

        if y - 1 >= 0:
            neighbors.append((x, y - 1, NORTH))
        if y + 1 < self.height:
            neighbors.append((x, y + 1, SOUTH))
        if x + 1 < self.width:
            neighbors.append((x + 1, y, EAST))
        if x - 1 >= 0:
            neighbors.append((x - 1, y, WEST))

        return (neighbors)

    def dfs_algo(self):
        visited = set()
        stack = []

        start = (0, 0)

        visited.add(start)
        stack.append(start)

        while stack:
            curr_x, curr_y = stack[-1]
            neighbors = self.get_neighbors(curr_x, curr_y)
        
            unvisited = []
            for neighbor in neighbors:
                nx, ny, direction = neighbor
                if (nx, ny) not in visited:
                    unvisited.append(neighbor)
            
            if unvisited:
                nx, ny, direction = random.choice(unvisited)
                self.remove_wall(curr_x, curr_y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def make_imperfect(self, extra_walls: int) -> None:
        walls_removed = 0
        max_attempts = extra_walls * 100

        attempts = 0

        while walls_removed < extra_walls and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            direction = random.choice([NORTH, SOUTH, EAST, WEST])
            dx, dy = DIRECTION_D[direction]
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                attempts += 1
                continue

            if self.has_wall(x, y, direction) and self.has_wall(nx, ny, OPPOSITE[direction]):
                self.remove_wall(x, y, direction)
                walls_removed += 1

            attempts += 1

    def display(self):
    # 1. Print the very top boundary of the maze
        print(" " + "___" * self.width)

        for y in range(self.height):
            # We start each row with the far-left wall
            output_str = "|"
            
            for x in range(self.width):
                # Check South wall (4) for the floor
                if self.has_wall(x, y, SOUTH):
                    char = "_"
                else:
                    char = " "
                    
                # Check East wall (2) for the side
                if self.has_wall(x, y, EAST):
                    sep = "|"
                else:
                    sep = " "
                    
                output_str += f"{char}{char}{sep}"
            
            print(output_str)
        