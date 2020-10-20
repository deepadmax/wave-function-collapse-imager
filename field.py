import numpy as np

from cardinals import *


class Tile:
    def __init__(self, states):
        self.states = states

    def __str__(self):
        if self.is_collapsed:
            return self.states[0]
        return '?'

    @property
    def is_collapsed(self):
        return self.entropy == 1

    @property
    def entropy(self):
        return len(self.states)


class Field:
    def __init__(self, patterns, width=20, height=11):
        self.width = width
        self.height = height
        
        self.patterns = patterns
        
        # Initialize matrix of Tiles
        self.tiles = [
            [
                Tile(self.patterns.keys())
                for x in range(self.width)
            ]
            for y in range(self.height)
        ]

    def __str__(self):
        return '\n'.join(
            ''.join(map(str, row))
            for row in self.tiles
        )

    @property
    def is_collapsed(self):
        return all(
            tile.is_collapsed
            for row in self.tiles
            for tile in row
        )

    def update_states(self, x, y):
        north = self.patterns[self.tiles[y-1][x]].faces[SOUTH]
        east  = self.patterns[self.tiles[y][x+1]].faces[WEST]
        south = self.patterns[self.tiles[y+1][x]].faces[NORTH]
        west  = self.patterns[self.tiles[y][x-1]].faces[EAST]

        unique_states = set(north) \
          .intersection(set(east)  \
          .intersection(set(south) \
          .intersection(set(west)
        )))

        states_dict = {
            state: sum([
                north.count(state),
                east.count(state),
                south.count(state),
                west.count(state)
            ])
            for state in unique_states
        }

        self.tiles[y][x].states = [
            state for state, count in states_dict.items()
            for n in range(count)
        ]

    def collapse(self):
        entropies = np.array([
            [None] * self.width
            for i in range(self.height)
        ])

        # Update entropies
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if not self.tiles[y][x].is_collapsed:
                    self.update_states(x, y)
                    entropies[y][x] = self.tiles[y][x].entropy

        # Coordinates of Tile with lowest entropy
        min_entropy_flatind = np.argmin(entropies)
        min_entropy_x = min_entropy_flatind % self.width
        min_entropy_y = min_entropy_flatind // self.height

        self.collapse_tile(min_entropy_x, min_entropy_y)

    def collapse_tile(self, x, y):
        # Collapse tile at (x, y) into one of its possible state
        self.tiles[y][x].states = [np.random.choice(self.tiles[y][x].states)]