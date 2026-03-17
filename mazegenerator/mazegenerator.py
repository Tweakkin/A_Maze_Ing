import curses
import random
from collections import deque
from typing import Any, Optional
from mazegenerator.maze_animation import animate_step

# constants representing the four wall directions of a cell
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# Maps each direction to its opposite direction
OPPOSITE = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST
}

# Maps each direction to its (dx, dy) movement offset
DIRECTION_D = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    EAST: (1, 0),
    WEST: (-1, 0)
}


# Main class that handles maze creation, solving, and file output
class MazeGenerator:

    # Initializes the maze grid and configuration from parsed config dict
    def __init__(self, parsed_dict: dict[str, Any]) -> None:
        # Validate that width is a positive integer
        if (
            not isinstance(parsed_dict['WIDTH'], int)
            or parsed_dict['WIDTH'] <= 0
        ):
            raise ValueError('width must be a positive integer!')
        # Validate that height is a positive integer
        if (
            not isinstance(parsed_dict['HEIGHT'], int)
            or parsed_dict['HEIGHT'] <= 0
        ):
            raise ValueError('height must be a positive integer!')
        self.config = parsed_dict
        # Set the random seed if provided for reproducible mazes
        if self.config.get('SEED') is not None:
            random.seed(self.config['SEED'])
        self.width = parsed_dict['WIDTH']
        self.height = parsed_dict['HEIGHT']
        # Initialize grid with all walls up (15 = all 4 bits set)
        self.grid = []
        for _ in range(self.height):
            temp = []
            for _ in range(self.width):
                temp.append(15)
            self.grid.append(temp)

    # Returns the wall value of a cell at (x, y)
    def get_cell(self, x: int, y: int) -> int:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(
                (
                    f"Cell ({x}, {y}) is out of bounds for "
                    f"{self.width}x{self.height} grid."
                )
            )
        return self.grid[y][x]

    # Checks if a specific wall exists on a cell at (x, y)
    def has_wall(self, x: int, y: int, wall_bit: int) -> bool:
        if wall_bit not in DIRECTION_D:
            raise ValueError(f"Invalid wall bit: {wall_bit}")

        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        return (self.grid[y][x] & wall_bit) != 0

    # Removes a wall between cell (x, y) and its neighbor in a dirc
    def remove_wall(self, x: int, y: int, direction: int) -> None:

        if direction not in DIRECTION_D:
            raise ValueError(
                (
                    f"Invalid direction: {direction}, Use NORTH, "
                    "SOUTH, EAST or WEST."
                )
            )

        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        # Remove the wall on the current cell side
        self.grid[y][x] = self.grid[y][x] & ~direction

        # Remove the wall on the neighbor cell side
        dx, dy = DIRECTION_D[direction]
        nx = x + dx
        ny = y + dy
        if 0 <= nx < self.width and 0 <= ny < self.height:
            self.grid[ny][nx] = self.grid[ny][nx] & ~OPPOSITE[direction]

    # Prints the raw grid array for debugging
    def print_grid(self) -> None:
        print(self.grid)

    # Returns list of neighbor cells reachable without crossing a wall
    def get_passable_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        passable = []

        for direc, (dx, dy) in DIRECTION_D.items():
            if not (self.has_wall(x, y, direc)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    passable.append((nx, ny))
        return passable

    # Returns all adjacent cells with their direction, regardless of walls
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

    # Generates the maze using DFS
    def dfs_algo(
        self,
        stdscr: Optional[curses.window] = None,
        animate: bool = False,
        delay: int = 20,
        theme_index: int = 0,
    ) -> None:
        visited: set[tuple[int, int]] = set()
        stack: list[tuple[int, int]] = []

        # Mark reserved cells ("42" pattern) as already visited
        reserved: set[tuple[int, int]] = getattr(self, 'reserved', set())
        visited.update(reserved)

        # Find a valid starting cell that is not reserved
        start = (0, 0)
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
        # Animate the initial state if animation is enabled
        if animate:
            animate_step(stdscr, self, delay, theme_index)

        # Main DFS loop: explore neighbors and passages
        while stack:
            curr_x, curr_y = stack[-1]
            neighbors = self.get_neighbors(curr_x, curr_y)

            # Filter to only unvisited and non-reserved neighbors
            unvisited = []
            for neighbor in neighbors:
                nx, ny, direction = neighbor
                if (nx, ny) not in visited and (nx, ny) not in reserved:
                    unvisited.append(neighbor)

            if unvisited:
                # Pick a random unvisited neighbor and create a passage
                nx, ny, direction = random.choice(unvisited)
                self.remove_wall(curr_x, curr_y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
                # Animate each carving step
                if animate:
                    animate_step(stdscr, self, delay, theme_index)
            else:
                # Backtrack if no unvisited neighbors remain
                stack.pop()
        # If maze is not perfect, remove extra walls to create loops
        if self.config['PERFECT'] is False:
            tot = int((self.height * self.width) * 0.1)
            self.make_imperfect(tot)
            # Animate the imperfect maze result
            if animate:
                animate_step(stdscr, self, delay, theme_index)

    # Removes extra walls to create multiple paths (imperfect maze)
    def make_imperfect(self, extra_walls: int) -> None:
        walls_removed = 0
        max_attempts = extra_walls * 100

        attempts = 0
        reserved: set[tuple[int, int]] = getattr(self, 'reserved', set())

        # Try to remove walls randomly until target is reached or max attempts
        while walls_removed < extra_walls and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            direction = random.choice([NORTH, SOUTH, EAST, WEST])
            dx, dy = DIRECTION_D[direction]
            nx, ny = x + dx, y + dy

            # Skip if neighbor is out of bounds
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                attempts += 1
                continue
            # Skip if either cell is reserved
            if (x, y) in reserved or (nx, ny) in reserved:
                attempts += 1
                continue

            # Only remove wall if both cells have exactly 3 walls
            if self.has_wall(x, y, direction) and self.has_wall(
                nx, ny, OPPOSITE[direction]
            ):
                if (
                    self.count_walls(x, y) == 3
                    and self.count_walls(nx, ny) == 3
                ):
                    self.remove_wall(x, y, direction)
                    walls_removed += 1

            attempts += 1

    # Reconstructs the path from BFS parent map, from exit back to start
    def find_path(
        self,
        mapped: dict[
            tuple[int, int], Optional[tuple[int, int]]
        ],
        exit: tuple[int, int],
    ) -> list[tuple[int, int]]:
        path = []
        curr: Optional[tuple[int, int]] = exit
        # Walk backwards through parent pointers to build the path
        while curr is not None:
            path.append(curr)
            curr = mapped[curr]
        return path[::-1]

    # Solves the maze using Breadth-First Search from start to exit
    def solve_bfs(
        self, start: tuple[int, int], exit: tuple[int, int]
    ) -> list[tuple[int, int]]:
        queue = deque([start])
        visited = {start}
        mapped: dict[tuple[int, int],
                     Optional[tuple[int, int]]] = {start: None}
        # Explore cells level by level until exit is found
        while queue:
            x, y = queue.popleft()
            if (x, y) == exit:
                return self.find_path(mapped, exit)
            neighbors = self.get_neighbors(x, y)
            # Add passable unvisited neighbors to the queue
            for dx, dy, direc in neighbors:
                if not self.has_wall(x, y, direc):
                    if (dx, dy) not in visited:
                        visited.add((dx, dy))
                        mapped[(dx, dy)] = (x, y)
                        queue.append((dx, dy))
        return []

    # Writes the maze grid, entry/exit, and solution path to a file
    def write_to_file(
        self, filename: str, path: list[tuple[int, int]]
    ) -> None:
        with open(filename, "w") as f:

            # SECTION 1: Write each row of the grid as hex characters
            for y in range(self.height):
                row = ""
                for x in range(self.width):
                    row += format(self.grid[y][x], 'X')  # 'X' = uppercase hex
                f.write(row + "\n")

            # Empty line to separate sections
            f.write("\n")

            # SECTION 2: Write entry and exit coordinates
            entry = self.config['ENTRY']
            exit = self.config['EXIT']
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit[0]},{exit[1]}\n")

            # SECTION 3: Convert the path into direction letters (N/S/E/W)
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

    # Embeds the "42" pattern into the maze grid as reserved cells
    def set_42(self) -> None:
        # Binary pattern representing the digits "42"
        pattern = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        p_height = len(pattern)
        p_width = len(pattern[0])
        # Check that the maze is large enough for the pattern
        if self.width < p_width or self.height < p_height:
            raise ValueError(
                (
                    "Maze too small for '42' pattern. "
                    f"Need at least {p_width}x{p_height}."
                )
            )
        # Center the pattern in the grid
        start_x = (self.width - p_width) // 2
        start_y = (self.height - p_height) // 2
        self.reserved = set()
        # Mark pattern cells as reserved and keep all walls up
        for row in range(p_height):
            for col in range(p_width):
                if pattern[row][col] == 1:
                    gx = start_x + col
                    gy = start_y + row
                    self.reserved.add((gx, gy))
                    self.grid[gy][gx] = 15

    # Counts the number of walls present on a cell at (x, y)
    def count_walls(self, x: int, y: int) -> int:
        count = 0
        for direction in [NORTH, SOUTH, EAST, WEST]:
            if self.has_wall(x, y, direction):
                count += 1
        return count
