import random
from mazegenerator import MazeGenerator

NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

OPPOSITE = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  WEST,
    WEST:  EAST
}

DIRECTION_D = {
    NORTH: (0, -1),
    SOUTH: (0,  1),
    EAST:  (1,  0),
    WEST:  (-1, 0)
}


class PrimGenerator(MazeGenerator):

    def prim_algo(self) -> None:
        in_maze  = set()
        reserved: set[tuple[int, int]] = getattr(self, 'reserved', set())

        start_x, start_y = 0, 0
        in_maze.add((start_x, start_y))

        frontier = self._get_frontier_walls(start_x, start_y, in_maze, reserved)

        while frontier:
            idx = random.randrange(len(frontier))
            frontier[idx], frontier[-1] = frontier[-1], frontier[idx]
            from_x, from_y, to_x, to_y, direction = frontier.pop()

            if (to_x, to_y) in in_maze or (to_x, to_y) in reserved:
                continue

            self.remove_wall(from_x, from_y, direction)
            in_maze.add((to_x, to_y))
            frontier.extend(self._get_frontier_walls(to_x, to_y, in_maze, reserved))

        if self.config.get('PERFECT') == False:
            tot = int((self.height * self.width) * 0.1)
            self.make_imperfect(tot)

    def _get_frontier_walls(self, x: int, y: int, in_maze: set, reserved: set) -> list:
        walls = []
        for direction, (dx, dy) in DIRECTION_D.items():
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in in_maze
                    and (nx, ny) not in reserved):
                walls.append((x, y, nx, ny, direction))
        return walls