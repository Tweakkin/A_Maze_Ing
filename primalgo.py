import random
import curses
from typing import Optional
from mazegenerator import MazeGenerator
from maze_animation import animate_step

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
    WEST:  (-1, 0),
}


class PrimGenerator(MazeGenerator):

    def prim_algo(self, stdscr: Optional[curses.window] = None, animate: bool = False, delay: int = 20, theme_index=0) -> None:
        in_maze  = set()
        reserved: set[tuple[int, int]] = getattr(self, 'reserved', set())

        start_x, start_y = 0, 0

        if (start_x, start_y) in reserved:
            found = False
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) not in reserved:
                        start_x, start_y = x, y
                        found = True
                        break
                if found:
                    break

        in_maze.add((start_x, start_y))

        if animate:
            animate_step(stdscr, self, delay, theme_index)

        frontier = self._get_frontier_walls(start_x, start_y, in_maze, reserved)

        while frontier:
            idx = random.randrange(len(frontier)) #return index
            frontier[idx], frontier[-1] = frontier[-1], frontier[idx]
            from_x, from_y, to_x, to_y, direction = frontier.pop()  

            if (to_x, to_y) in in_maze or (to_x, to_y) in reserved:
                continue

            self.remove_wall(from_x, from_y, direction)
            in_maze.add((to_x, to_y))
            frontier.extend(self._get_frontier_walls(to_x, to_y, in_maze, reserved))

            if animate:
                animate_step(stdscr, self, delay, theme_index)
        
        if self.config.get('PERFECT') == False:
            tot = int((self.height * self.width) * 0.05) #10
            self.make_imperfect(tot)

            if animate:
                animate_step(stdscr, self, delay, theme_index)

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
    