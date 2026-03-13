import curses
import random
from collections import deque
from typing import Optional
from mazegenerator.maze_animation import animate_step

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

    def get_cell(self, x: int, y: int) -> int:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(
                f"Cell ({x}, {y}) is out of bounds for {self.width}x{self.height} grid.")
        return self.grid[y][x]
    # change (add)
    # def set_entry_exit(self):
    #     x_entry, y_entry = self.config['ENTRY']
    #     x_exit, y_exit = self.config['EXIT']

    #     if y_entry == 0:
    #         self.remove_wall(x_entry, y_entry, NORTH)
    #     elif y_entry == self.height - 1:
    #         self.remove_wall(x_entry, y_entry, SOUTH)
    #     elif x_entry == 0:
    #         self.remove_wall(x_entry, y_entry, WEST)
    #     elif x_entry == self.width - 1:
    #         self.remove_wall(x_entry, y_entry, EAST)

    #     if y_exit == 0:
    #         self.remove_wall(x_exit, y_exit, NORTH)
    #     elif y_exit == self.height - 1:
    #         self.remove_wall(x_exit, y_exit, SOUTH)
    #     elif x_exit == 0:
    #         self.remove_wall(x_exit, y_exit, WEST)
    #     elif x_exit == self.width - 1:
    #         self.remove_wall(x_exit, y_exit, EAST)

    def has_wall(self, x: int, y: int, wall_bit: int) -> bool:
        if wall_bit not in DIRECTION_D:
            raise ValueError(f"Invalid wall bit: {wall_bit}")

        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        return (self.grid[y][x] & wall_bit) != 0

    def remove_wall(self, x: int, y: int, direction: int) -> None:

        if direction not in DIRECTION_D:
            raise ValueError(
                f"Invalid direction: {direction}, Use NORTH, SOUTH, EAST or WEST.")

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

    def get_passable_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        passable = []

        for direc, (dx, dy) in DIRECTION_D.items():
            if not (self.has_wall(x, y, direc)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    passable.append((nx, ny))
        return passable

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int, int]]:
        neighbors: list[tuple[int, int, int]] = []

        if y - 1 >= 0:
            neighbors.append((x, y - 1, NORTH))
        if y + 1 < self.height:
            neighbors.append((x, y + 1, SOUTH))
        if x + 1 < self.width:
            neighbors.append((x + 1, y, EAST))
        if x - 1 >= 0:
            neighbors.append((x - 1, y, WEST))

        return neighbors

    def dfs_algo(self, stdscr: Optional[curses.window] = None, animate: bool = False, delay: int = 20, theme_index=0) -> None:
        visited: set[tuple[int, int]] = set()
        stack: list[tuple[int, int]] = []

        reserved: set[tuple[int, int]] = getattr(self, 'reserved', set())
        visited.update(reserved)

        start = (0, 0)
    # add
        if start in reserved:
            found = False
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) not in reserved:
                        start = (x, y)
                        found = True
                        break
                if found:
                    break

        visited.add(start)
        stack.append(start)
    # add
        if animate:
            animate_step(stdscr, self, delay, theme_index)

        while stack:
            curr_x, curr_y = stack[-1]
            neighbors = self.get_neighbors(curr_x, curr_y)

            unvisited = []
            for neighbor in neighbors:
                nx, ny, direction = neighbor
                if (nx, ny) not in visited and (nx, ny) not in reserved:
                    unvisited.append(neighbor)

            if unvisited:
                nx, ny, direction = random.choice(unvisited)
                self.remove_wall(curr_x, curr_y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            # add
                if animate:
                    animate_step(stdscr, self, delay, theme_index)
            else:
                stack.pop()
        if self.config['PERFECT'] == False:
            tot = int((self.height * self.width) * 0.1)
            self.make_imperfect(tot)
        # add
            if animate:
                animate_step(stdscr, self, delay, theme_index)

    def make_imperfect(self, extra_walls: int) -> None:
        walls_removed = 0
        max_attempts = extra_walls * 100

        attempts = 0
        reserved: set[tuple[int, int]] = getattr(self, 'reserved', set())

        while walls_removed < extra_walls and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            direction = random.choice([NORTH, SOUTH, EAST, WEST])
            dx, dy = DIRECTION_D[direction]
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.width and 0 <= ny < self.height):
                attempts += 1
                continue
            if (x, y) in reserved or (nx, ny) in reserved:
                attempts += 1
                continue

            if self.has_wall(x, y, direction) and self.has_wall(nx, ny, OPPOSITE[direction]):
                if self.count_walls(x, y) == 3 and self.count_walls(nx, ny) == 3:
                    self.remove_wall(x, y, direction)
                    walls_removed += 1

            attempts += 1

    def find_path(self, mapped: dict, exit: tuple[int, int]) -> list[tuple[int, int]]:
        path = []
        curr = exit
        while curr is not None:
            path.append(curr)
            curr = mapped[curr]
        return path[::-1]

    def solve_bfs(self, start: tuple[int, int], exit: tuple[int, int]) -> list[tuple[int, int]]:
        queue = deque([start])
        visited = {start}
        mapped: dict[tuple[int, int],
                     Optional[tuple[int, int]]] = {start: None}
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

    def write_to_file(self, filename: str, path: list[tuple[int, int]]) -> None:
        with open(filename, "w") as f:

            # SECTION 1: Write the grid as hex
            # Each cell value (0-15) becomes a hex character (0-F)
            # Example: cell value 12 -> 'C', cell value 10 -> 'A'
            for y in range(self.height):
                row = ""
                for x in range(self.width):
                    row += format(self.grid[y][x], 'X')  # 'X' = uppercase hex
                f.write(row + "\n")

            # Empty line to separate sections
            f.write("\n")

            # SECTION 2: Entry and exit coordinates
            entry = self.config['ENTRY']
            exit = self.config['EXIT']
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit[0]},{exit[1]}\n")

            # SECTION 3: Path as direction letters
            # Compare each cell with the next cell in the path
            # to determine which direction was taken
            directions = ""
            for i in range(len(path) - 1):
                cx, cy = path[i]      # current cell
                nx, ny = path[i + 1]  # next cell
                dx = nx - cx  # horizontal movement
                dy = ny - cy  # vertical movement
                if dx == 1:       # moved right
                    directions += "E"
                elif dx == -1:    # moved left
                    directions += "W"
                elif dy == 1:     # moved down
                    directions += "S"
                elif dy == -1:    # moved up
                    directions += "N"
            f.write(directions + "\n")

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
        if self.width < p_width or self.height < p_height:
            raise ValueError(
                f"Maze too small for '42' pattern. Need at least {p_width}x{p_height}.")
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
