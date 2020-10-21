import numpy as np
from random import randint, choice

from .tiles import Tile
from .patterns import Pattern


class Board:
    def __init__(self, width: int = 0, height: int = 0):
        self.width, self.height = width, height
        self.possible_states = []
        self.grid = [[Tile((i, j), self.possible_states) for j in range(width)] for i in range(height)]
        self.pattern = Pattern()
        self.N = 1

    def __str__(self):
        return "\n".join(["".join([*map(str, row)]) for row in self.grid])

    def is_completed(self):
        return all([all([*map(lambda a: a.has_collapsed, row)]) for row in self.grid])

    def load_patterns(self):
        for i in range(self.height):
            for j in range(self.width):
                patt = []
                for _i in range(-self.N, self.N+1):
                    patt.append([])
                    for _j in range(-self.N, self.N+1):
                        patt[_i+self.N].append(str(self.grid[(i+_i)%self.height][(j+_j)%self.width]))
                self.pattern.add_pattern(patt[self.N][self.N], patt)

    def seed(self):
        self.grid[randint(0,self.height-1)][randint(0,self.width-1)].states = [choice(self.possible_states)]

    def load_from_file(self, file_name: str):
        """loads a board from a file ('file_name') and extracts all possible states"""
        with open(file_name, 'r') as file:
            self.grid = [list(row) for row in file.read().split('\n')]

            self.height = len(self.grid)
            self.width  = len(self.grid[0])
            for i in range(self.height):
                for j in range(self.width):
                    elt = self.grid[i][j]

                    self.grid[i][j] = Tile((i, j), [elt])

                    if not elt in self.possible_states:
                        self.possible_states.append(elt)

    def clear(self):
        """clears the board and sets the state for every position to every possible state (superposition)"""
        self.grid = [[Tile((i, j), self.possible_states) for j in range(self.width)] for i in range(self.height)]

    def get_neighbors(self, u: int = 0, v: int = 0):
        """return neighbours around a tile"""
        neighbors = []
        for i in range(-self.N, self.N+1):
            for j in range(-self.N, self.N+1):
                neighbors.append(((i+u) % self.height, (j+v) % self.width))
        return neighbors

    def get_states_of_neighbors(self, ij: tuple = (0,0)):
        neighbors = self.get_neighbors(ij, self.N)
        states = [self.grid[i][j].states for i,j in neighbors]
        return states

    def get_lowest_entropy(self):
        # Generate grid of entropy for each tile
        entropy_grid = np.array([
            [
                entr if (entr := self.grid[i][j].get_entropy()) != 1
                else len(self.possible_states) + 1
                for j in range(self.width)
            ]
            for i in range(self.height)
        ])

        # Find the lowest entropy
        min_entropy = np.min(entropy_grid)

        # All the indices which contain the minimum entropy
        coords = [(int(i), int(j)) for i, j in  zip(*np.where(entropy_grid == min_entropy))]
        
        # Pick a random element
        n = np.random.randint(len(coords))
        i, j = coords[n]

        return i, j

    def generate(self):
        while not self.is_completed():
            lowest = self.get_lowest_entropy()
            # print(lowest)
            self.grid[lowest[0]][lowest[1]].collapse()

            neighbors = self.get_neighbors(lowest[0], lowest[1])
            active = neighbors
            while len(active) > 0:
                # print(len(active))
                new_active = []
                
                grid = self.grid[:]

                for i, j in active:
                    # grid[i][j].states = ['X']
                    if not self.grid[i][j].has_collapsed:
                        neighbors = self.get_neighbors(i, j)
                        neighbor_tiles = [self.grid[u][v] for u, v in neighbors]

                        k_size = self.N*2 + 1
                        # print(k_size)
                        new_states = self.pattern.match([
                          neighbor_tiles[k_size * n : k_size * (n + 1)]
                          for n in range(k_size)
                        ])
                        
                        _states = self.grid[i][j].states
                        _states = set(s*_states.count(s) for s in _states)

                        _new_states = set(s*new_states.count(s) for s in new_states)

                        #print(f"NEW: {_new_states}")
                        #print(f"OLD: {_states}")
                        
                        #if set(self.grid[i][j].states) != set(new_states):
                        if _states != _new_states:
                            self.grid[i][j].update_states(new_states)
                            new_active += list(set(neighbors).difference(set(active)))
                    grid[i][j].collapse()

                print(self, end="\n\n")

                active = list(set(new_active))