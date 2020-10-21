from .tiles import Tile
from .patterns import Pattern
from random import randint, choice

class Board:
    def __init__(self, width: int = 0, height: int = 0):
        self.width, self.height = width, height
        self.possible_states = []
        self.grid = [[Tile((i, j), self.possible_states) for j in range(width)] for i in range(height)]
        self.pattern = Pattern()
        self.N = 2

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
        self.grid[randint(0,self.height)][randint(0,self.width)].states = choice(self.possible_states)

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

    def get_neighbours(self, ij: tuple = (0,0)):
        """return neighbours around a tile"""
        neighbours = []
        for i in range(-self.N, self.N+1):
            for j in range(-self.N, self.N+1):
                if i != 0 or j != 0:
                    neighbours.append((i, j))
        return neighbours

    def get_states_of_neighbours(self, ij: tuple = (0,0)):
        neighbours = self.get_neighbours(ij, self.N)
        states = [self.grid[i][j].states for i,j in neighbours]
        return states

    def get_lowes_entropy(self):
        entropy_grid = []
        for i in range(self.height):
            entropy_grid.append([])
            for j in range(self.width):
                entropy_grid[i].append(self.grid[i][j].get_entropy())
        entropy_vec = [row.index(min(row)) for row in entropy_grid]
        entropy_vec_ = [entropy_grid[i][entropy_vec[i]] for i in range(self.height)]
        x = entropy_vec_.index(min(entropy_vec_))
        y = entropy_vec[entropy_vec_.index(min(entropy_vec_))]
        return (x, y)

    def generate(self):
        while not self.is_completed():
            lowest = self.get_lowes_entropy()

            self.grid[lowest[0]][lowest[1]].collapse()

            neighbours = self.get_neighbours(lowest)
            active = neighbours
            while len(active) > 0:
                new_active = []
                for elt in active:
                    if not self.grid[elt[0]][elt[1]].has_collapsed:
                        neighbours = self.get_neighbours(elt)
                        # print(neighbours)
                        neighbour_states = [self.grid[i][j] for i,j in neighbours]
                        new_states = self.pattern.match([neighbour_states[(self.N*2+1)*i:(self.N*2+1)*i+self.N*2+1] for i in range(self.N*2+1)])

                        if self.grid[elt[0]][elt[1]].states != new_states:
                            self.grid[elt[0]][elt[1]].update_states(new_states)
                            new_active = neighbours

                active = new_active

            print(self)
            break