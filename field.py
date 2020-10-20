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
        self.update_entropy()

        for row in self.entropies:
            for tile in row:
                if tile is None or not tile.is_collapsed:
                    return False
            return True

    def update_states(self, x, y):
        print('About to sort faces')
        # north, east, west, south = [
        #     [
        #         x for state in self.tiles[j][i].states
        #         for face in self.patterns[state].faces
        #         for x in face
        #     ]
        #     for i, j in cardinal_coordinates(x, y)
        # ]

        north, east, west, south = [
            list(self.patterns.keys())
            for i, j in cardinal_coordinates(x, y)
        ]
        
        print(north)

        print('Faces sorted')

        # north = self.patterns[self.tiles[y-1][x].id].faces[SOUTH]
        # east  = self.patterns[self.tiles[y][x+1].id].faces[WEST]
        # south = self.patterns[self.tiles[y+1][x].id].faces[NORTH]
        # west  = self.patterns[self.tiles[y][x-1].id].faces[EAST]

        unique_states = set(north) \
          .intersection(set(east)  \
          .intersection(set(south) \
          .intersection(set(west)
        )))
        print('Unique states')

        states_dict = {
            state: sum([
                north.count(state),
                east.count(state),
                south.count(state),
                west.count(state)
            ])
            for state in unique_states
        }
        print('States dict')

        self.tiles[y][x].states = [
            state for state, count in states_dict.items()
            for n in range(count)
        ]
        print('States updated')

    def update_entropy(self):
        self.entropies = np.array([
            [None] * self.width
            for i in range(self.height)
        ])

        print('Updating entropies!')
        
        # Update entropies
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                print('in loop')
                if not self.tiles[y][x].is_collapsed:
                    print(f'[{x}][{y}] not collapsed')
                    self.update_states(x, y)
                    self.entropies[y][x] = self.tiles[y][x].entropy

        self.entropies = self.entropies[1:-1,1:-1]

    def collapse(self):
        print('Collapsing now!')
        while not self.is_collapsed:
            print('Not yet collapsed...')
            # Coordinates of Tile with lowest entropy
            print(f'Entropies: {self.entropies}')
            min_entropy_flatind = np.argmin(self.entropies)
            min_entropy_x = min_entropy_flatind % self.width
            min_entropy_y = min_entropy_flatind // self.height

            entropy = sum([
                sum([e if e else len(self.patterns.keys()) for e in row])
                for row in self.entropies
            ])
            print(f'Total entropy: {entropy}')

            self.collapse_tile(min_entropy_x, min_entropy_y)

    def collapse_tile(self, x, y):
        # Collapse tile at (x, y) into one of its possible state
        self.tiles[y][x].states = [np.random.choice(self.tiles[y][x].states)]