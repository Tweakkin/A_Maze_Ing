class Maze:
    N = 0b0001 #LFO9
    E = 0b0010 #LIMAN
    S = 0b0100 #LTA7T
    W = 0b1000 #LISSAR

    OPPOSITE = {N: S, S: N, E: W, W: E}

    DELTA = {
        N: (0, -1),
        E: (0, 1),
        S: (1, 0),
        W: (-1, 0),
    }

    def __init__(self, width, height, entry, exit_):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_

        self.grid = [[0xf] * width for _ in range(height)]
    
    def remove_wall(self, x, y, direction):
        self.grid[y][x] &= ~direction