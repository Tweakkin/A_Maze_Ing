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

    def __init__(self, parsed_dict: dict) -> None:
        if not isinstance(parsed_dict['WIDTH'], int) or parsed_dict['WIDTH'] <= 0:
            raise ValueError('width must be a positive integer!')
        if not isinstance(parsed_dict['HEIGHT'], int) or parsed_dict['HEIGHT'] <= 0:
            raise ValueError('height must be a positive integer!')
        self.config = parsed_dict
        self.width = parsed_dict['WIDTH']
        self.height = parsed_dict['HEIGHT']
        self.grid = []
        for _ in range(self.height):
            temp = []
            for _ in range(self.width):
                temp.append(15)
            self.grid.append(temp)
    
    def get_cell(self, x:int, y:int) -> int:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Cell ({x}, {y}) is out of bounds for {self.width}x{self.height} grid.")
        return self.grid[y][x]
    
    def set_entry_exit(self):
        x_entry, y_entry = self.config['ENTRY']
        x_exit, y_exit = self.config['EXIT']
        
        if y_entry == 0:
            self.remove_wall(x_entry, y_entry, NORTH)
        elif y_entry == self.height - 1:
            self.remove_wall(x_entry, y_entry, SOUTH)
        elif x_entry == 0:
            self.remove_wall(x_entry, y_entry, WEST)
        elif x_entry == self.width - 1:
            self.remove_wall(x_entry, y_entry, EAST)
        
        if y_exit == 0:
            self.remove_wall(x_exit, y_exit, NORTH)
        elif y_exit == self.height - 1:
            self.remove_wall(x_exit, y_exit, SOUTH)
        elif x_exit == 0:
            self.remove_wall(x_exit, y_exit, WEST)
        elif x_exit == self.width - 1:
            self.remove_wall(x_exit, y_exit, EAST)


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


        if hasattr(self, 'reserved'):
            visited.update(self.reserved)
        start = (0, 0)

        visited.add(start)
        stack.append(start)

        while stack:
            curr_x, curr_y = stack[-1]
            neighbors = self.get_neighbors(curr_x, curr_y)
        
            unvisited = []
            for neighbor in neighbors:
                nx, ny, direction = neighbor
                if (nx, ny) not in visited and (nx, ny) not in self.reserved:
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

    def set_42(self):
        pattern = [
            [1, 0, 0, 1, 0, 1, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 1, 1, 1],
        ]

        p_height = len(pattern)
        p_width = len(pattern[0])
        # Calculate the top-left corner so the pattern is centered
        start_x = (self.width - p_width) // 2
        start_y = (self.height - p_height) // 2
        # Store the reserved cells in a set for later use
        self.reserved = set()
        for row in range(p_height):
            for col in range(p_width):
                if pattern[row][col] == 1:
                    gx = start_x + col
                    gy = start_y + row
                    self.reserved.add((gx, gy))
                    # Set cell to 0 (all walls removed) so it looks like
                    # an open block — a "room" that forms the "42"
                    self.grid[gy][gx] = 0

    def display(self):
        # Print the top border, reflecting actual NORTH walls
        top_row = " "
        for x in range(self.width):
            if not self.has_wall(x, 0, NORTH):
                top_row += "   "
            else:
                top_row += "___"
        print(top_row)

        for y in range(self.height):
            row = ""
            for x in range(self.width):
                # WEST wall: only print '|' if wall exists
                if x == 0:
                    if self.has_wall(x, y, WEST):
                        row += "|"
                    else:
                        row += " "
                # SOUTH wall: print '_' if wall exists, else space
                if self.has_wall(x, y, SOUTH):
                    row += "_"
                else:
                    row += " "
                # EAST wall: print '|' if wall exists, else space
                if self.has_wall(x, y, EAST):
                    row += "|"
                else:
                    row += " "
            print(row)

        # Print the bottom border, reflecting actual SOUTH walls
        bottom_row = " "
        for x in range(self.width):
            if self.has_wall(x, self.height - 1, SOUTH):
                bottom_row += "___"
            else:
                bottom_row += "   "
        print(bottom_row)
            