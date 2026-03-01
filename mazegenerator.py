import random
from collections import deque
from typing import Optional

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
    

    def get_passable_neighbors(self, x: int, y: int) -> list:
        passable = []

        for direc, (dx, dy) in DIRECTION_D.items():
            if not (self.has_wall(x, y, direc)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    passable.append((nx, ny))
        return passable

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

    def dfs_algo(self) -> None:
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
        if self.config['PERFECT'] == False:
            tot = int((self.height * self.width) * 0.1)
            self.make_imperfect(tot)
        

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
            if (x, y) in self.reserved or (nx, ny) in self.reserved:
                attempts += 1
                continue

            if self.has_wall(x, y, direction) and self.has_wall(nx, ny, OPPOSITE[direction]):
                if self.count_walls(x, y) == 3 or self.count_walls(nx, ny) == 3:
                    self.remove_wall(x, y, direction)
                    walls_removed += 1

            attempts += 1

    def find_path(self, mapped: dict, exit: tuple[int, int]) -> list:
        path = []
        curr = exit
        while curr is not None:
            path.append(curr)
            curr = mapped[curr]
        return path[::-1]

    def solve_bfs(self, start: tuple[int, int], exit: tuple[int, int]) -> list:
        queue = deque([start])
        visited = {start}
        mapped: dict[tuple[int, int], Optional[tuple[int, int]]] = {start: None}
        while queue:
            x, y = queue.popleft()
            if (x, y) == exit:
                return self.find_path(mapped, exit)
            neighbors = self.get_neighbors(x, y)
            for dx, dy, direc in neighbors:
                if not self.has_wall(x, y, direc):
                    if (dx, dy) not in visited:
                        visited.add((dx, dy))
                        mapped[(dx, dy)] = (x, y)
                        queue.append((dx, dy))
        return []

    def set_42(self) -> None:
        pattern = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        p_height = len(pattern)
        p_width = len(pattern[0])
        start_x = (self.width - p_width) // 2
        start_y = (self.height - p_height) // 2
        self.reserved = set()
        for row in range(p_height):
            for col in range(p_width):
                if pattern[row][col] == 1:
                    gx = start_x + col
                    gy = start_y + row
                    self.reserved.add((gx, gy))
                    self.grid[gy][gx] = 15

    def count_walls(self, x: int, y: int) -> int:
        count = 0
        for direction in [NORTH, SOUTH, EAST, WEST]:
            if self.has_wall(x, y, direction):
                count += 1
        return count



# class BfsAlgo(MazeGenerator):
    
#     def find_path(self, mapped, exit):
#         path = []
#         curr = exit
#         while curr is not None:
#             path.append(curr)
#             curr = mapped[curr]
#         return path[::-1]

#     def solve_bfs(self, start, exit):
#         queue = deque([start])
#         visited = {start}
#         mapped = {start: None}
#         while queue:
#             x, y = queue.popleft()
#             if (x, y) == exit:
#                 return self.find_path(mapped, exit)
#             neighbors = self.get_neighbors(x, y)
#             for dx, dy, direc in neighbors:
#                 if not self.has_wall(x, y, direc):
#                     if (dx, dy) not in visited:
#                         visited.add((dx, dy))
#                         mapped[(dx, dy)] = (x, y)
#                         queue.append((dx, dy))
#         return []