import numpy as np

from rich import print

from .matcher import Matcher
from .tile import Tile


class Field:
    def __init__(self, patterns, matcher, N=1, width=1, height=1):
        self.matcher = matcher

        self.N = N
        self.width = width
        self.height = height

        self.patterns = patterns
        # self.patterns = {k:v for k,v in zip(pattern_index, range(len(pattern_index)))}
        
        # Initialize an empty canvas
        self.clear()

    @classmethod
    def create(cls, fname, N=1, width=10, height=7, rotations=False):
        """Create a canvas from file"""

        with open(fname) as f:
            # A 2D array of values
            value_grid = [list(row) for row in f.read().split('\n')]

            # width and height of the value grid
            value_grid_width = len(value_grid[0])
            value_grid_height = len(value_grid)
            
            # a dictionary of patterns used for indexing
            patterns = {}
            # a list of patterns used for indexing
            in_patterns = []

            # looping over every single value
            for i in range(value_grid_height):
                for j in range(value_grid_width):
                    # gather the NxN grid of values to for a pattern
                    neighbors = tuple(
                        tuple(
                            value_grid[(i + u) % value_grid_height][(j + v) % value_grid_width]
                            for v in range(N)
                        )
                        for u in range(N)
                    )

                    if rotations:
                        # Add pattern with all four different orientations
                        for _ in range(4):
                            neighbors = tuple(tuple(row) for row in np.rot90(neighbors, k=1))
                            # if this pattern is not already in the index, save it
                            if neighbors not in patterns:
                                patterns[neighbors] = len(in_patterns)
                                in_patterns += [neighbors]
                    else:
                        # if this pattern is not already in the index, save it
                        if neighbors not in patterns:
                            patterns[neighbors] = len(in_patterns)
                            in_patterns += [neighbors]

            # a grid indecies of patterns 
            pattern_grid = [[patterns[tuple(tuple(
                            value_grid[(i + u) % value_grid_height][(j + v) % value_grid_width]
                            for v in range(N))for u in range(N))] for j in range(value_grid_width)] for i in range(value_grid_height)]
            
            # Initialize Matcher
            matcher = Matcher()

            # gets the relative cardinal coordinates in a 2d array
            cardinals = lambda i,j: [(i, j-1), (i+1, j), (i, j+1), (i-1, j)]

            # loop over every pattern index and add all it's cardinal 
            # neighbors to the matcher
            for i in range(value_grid_height):
                for j in range(value_grid_width):
                    # get the neighbors cardinal neighbors
                    neighbors = [
                        pattern_grid[u%value_grid_height][v%value_grid_width]
                        for u,v in cardinals(i,j)
                    ]
                    # add them to the matcher
                    matcher.add_pattern(neighbors, pattern_grid[i][j])

            print(f'number of different {N}x{N} patterns: {len(patterns)}')

            # return a new instance of a Filed initialized with correct parameters
            return cls(in_patterns, matcher, N, width, height)

    def __str__(self):
        output = ""
        for row in self.canvas:
            for elt in row:
                tile = str(elt)
                if tile not in ['multi', 'none']:
                    output += self.patterns[int(tile)][0][0]
                else:
                    if tile == 'multi':
                        output += '░'
                    elif tile == 'none':
                        output += '!'
            output += "\n"
        output = output[:-1]
        return output

    @property
    def has_collapsed(self):
        """Check if all tiles have had their states collapsed"""
        
        for row in self.canvas:
            for tile in row:
                if not tile.has_collapsed:
                    return False
        return True

    def clear(self):
        """Clear the canvas and set all tiles into superposition"""
        
        self.canvas = [
            [
                Tile(
                    states=list(range(len(self.patterns))) # indecies of all the patterns
                ) 
                for j in range(self.width)
            ]
            for i in range(self.height)
        ]

    def seed(self):
        """Collapse the state of a random tile"""
        
        i = np.random.randint(0, self.height)
        j = np.random.randint(0, self.width)
        self.canvas[i][j].collapse()

    def get_lowest_entropy(self):
        """Get the index for the lowest entropy tile"""

        # Generate a grid of the entropy for each tile
        entropies = np.array([
            [
                self.canvas[i][j].entropy if not self.canvas[i][j].has_collapsed else -1
                for j in range(self.width)
            ]
            for i in range(self.height)
        ])

        # Find the highest entropy
        max_entropy = np.max(entropies)
        entropies[entropies == -1] = max_entropy + 1

        # Find the lowest entropy
        min_entropy = np.min(entropies)

        # All the indices which contain the minimum entropy
        indices = [(int(i), int(j)) for i, j in  zip(*np.where(entropies == min_entropy))]
        
        # Pick a random element
        n = np.random.randint(len(indices))
        i, j = indices[n]

        return (i, j)

    def get_neighbors(self, u, v):
        """Get indices of neighboring tiles at (i, j)"""

        N = lambda i,j: [(i, j-1), (i+1, j), (i, j+1), (i-1, j)]
        
        neighbors = [
            (
                i % self.height,
                j % self.width
            )
            for i,j in N(u,v)
        ]

        return neighbors

    def collapse(self):
        """Until all tiles on the canvas have had their states collapsed,
        continue to propagate the collapse from the tile of lowest entropy
        """

        while not self.has_collapsed:
            min_i, min_j = self.get_lowest_entropy()

            if not self.canvas[min_i][min_j].has_collapsed:
                self.canvas[min_i][min_j].collapse()

            # Continue until there are no more affected tiles
            affected = self.get_neighbors(min_i, min_j)

            total_updated = 0
            while len(affected) > 0:
                new_affected = []

                # Go through all currently affected tiles
                for i, j in affected:
                    # print('wowieee!')
                    if not self.canvas[i][j].has_collapsed:
                        neighbors = self.get_neighbors(i, j)
                        neighbor_tiles = [
                            self.canvas[u][v].states
                            for u,v in neighbors
                        ]

                        # Calculate the new states of (i, j) based on its neighbors
                        new_states = self.matcher.match(neighbor_tiles)

                        # If the new states are different to the current ones,
                        # update the states for (i, j) and add neighbors to affected
                        current_states = self.canvas[i][j].states
                        
                        if tuple(current_states) != new_states:
                            if len(list(set(new_states))) == 1:
                                self.canvas[i][j].states = [new_states[0]]
                            else:
                                self.canvas[i][j].states = new_states
                            # self.canvas[i][j].states = list(set(new_states))
                            # print(new_states)
                            
                            new_affected += [
                                pos for pos in set(neighbors).difference(set(affected))
                                if pos not in new_affected and pos not in affected
                            ]

                            total_updated += 1

                        if len(new_states) == 0:
                            print('errrr!!! line 231')


                affected = []
                if len(new_affected) > 0:
                    affected = new_affected[:]
                    
            print('total updated: ',total_updated)
            print(str(self).replace('!', "[red]![/red]"), '\n')
            
        if str(self).count('!'):
            return False
        return True