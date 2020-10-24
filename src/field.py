import numpy as np

from rich import print

from .matcher import Matcher
from .tile import Tile


def cardinals(i, j):
    return ((i, j-1), (i+1, j), (i, j+1), (i-1, j))


class Field:
    def __init__(self, patterns, matcher, N=1, width=1, height=1, errchar='§'):
        self.patterns = patterns
        self.matcher = matcher

        self.N = N
        self.width = width
        self.height = height

        # The character displayed for tiles which have raised an error
        self.errchar = errchar
        
        # Initialize an empty canvas
        self.clear()

    @classmethod
    def create_from_file(cls, fname, **kwargs):
        """Load a text file as a 2D array
        and create a Field from the characters
        """

        with open(fname) as f:
            # Turn individual characters into items in a 2D array
            value_grid = [list(row) for row in f.read().split('\n')]

            return cls.create(value_grid, **kwargs)

    @classmethod
    def create(cls, value_grid, N=1, width=10, height=7, symmetry=True):
        """Create a Field from a value grid"""

        # width and height of the value grid
        value_grid_width = len(value_grid[0])
        value_grid_height = len(value_grid)
        
        # Dictionary of patterns used for indexing
        patterns = {}
        # List of patterns used for indexing
        in_patterns = []

        # Looping over every single value
        for i in range(value_grid_height):
            for j in range(value_grid_width):
                # Gather the NxN grid of values for a pattern
                neighbors = tuple(
                    tuple(
                        value_grid[(i + u) % value_grid_height][(j + v) % value_grid_width]
                        for v in range(N)
                    ) for u in range(N)
                )

                # Include mirror images and all four different orientations for each
                if symmetry:
                    # The two mirror flips
                    for _flip in range(2):
                        neighbors = tuple(tuple(row) for row in np.flip(neighbors))
                        
                        # The four different orientations
                        for _rotate in range(4):
                            neighbors = tuple(tuple(row) for row in np.rot90(neighbors, k=1))

                            if neighbors not in in_patterns:
                                patterns[neighbors] = len(patterns)
                                in_patterns.append(neighbors)
                
                # Do not include all that fancy nonsense and store it plainly
                else:
                    neighbors = tuple(tuple(row) for row in neighbors)

                    if neighbors not in in_patterns:
                        patterns[neighbors] = len(patterns)
                        in_patterns.append(neighbors)

        # a grid indicies of patterns (
        #   Is this comment correct? It looks whack and grammatically incorrect,
        #   so I thought I'd ask you.
        # )
        pattern_grid = [
            [
                patterns[
                    tuple(
                        tuple(
                            value_grid[(i + u) % value_grid_height][(j + v) % value_grid_width]

                            for v in range(N)
                        ) for u in range(N)
                    )
                        
                ] for j in range(value_grid_width)
            ] for i in range(value_grid_height)
        ]

        # Initialize Matcher
        matcher = Matcher()

        # Generate patterns for the Matcher
        # This means the cardinal neighbors of patterns,
        # as opposed to neighbors of tiles
        for i in range(value_grid_height):
            for j in range(value_grid_width):
                # Get the neighbors' cardinal neighbors
                neighbors = [
                    pattern_grid[u % value_grid_height][v % value_grid_width]
                    for u, v in cardinals(i, j)
                ]
                # Add them to the Matcher
                matcher.add_pattern(neighbors, pattern_grid[i][j])

        print(f'Loaded {len(patterns)} patterns of size {N}×{N}')

        # Return a new instance of a Field
        # initialized with the generated parameters
        return cls(in_patterns, matcher, N, width, height)

    def __str__(self):
        output = ""
        for row in self.canvas:
            for tile in row:
                state = tile.get_state()
                
                try:
                    if state:
                        output += self.patterns[state][0][0]
                    else:
                        output += '░'

                except RuntimeError:
                    output += self.errchar

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
                    states=range(len(self.patterns)) # indicies of all the patterns
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

    def get_neighbors(self, i, j):
        """Get indices of neighboring tiles at (i, j)"""
        
        neighbors = [
            (
                u % self.height,
                v % self.width
            )
            for u, v in cardinals(i, j)
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
                            self.canvas[i][j].update_states(new_states)
                            
                            new_affected += [
                                pos for pos in set(neighbors).difference(set(affected))
                                if pos not in new_affected and pos not in affected
                            ]

                affected = new_affected
        
        # Return False if there are any erroneous tiles
        if str(self).count(self.errchar):
            return False

        return True

    def validate(self):
        """Check whether the generated canvas follows the rules accordingly"""
        
        if not self.has_collapsed:
            self.collapse()

        canvas = np.array(self.canvas)

        for i in range(self.height - self.N):
            for j in range(self.width - self.N):
                # If no patterns can be matched at a particular section,
                # the canvas has not generated a valid configuration
                neighbors = tuple(
                    tuple(
                        self.patterns[canvas[
                            (i + u) % self.height,
                            (j + v) % self.width
                        ].get_state()][0][0]
                        
                        for v in range(self.N)
                    )
                    for u in range(self.N)
                )

                if neighbors not in self.patterns:                        
                    return False
                    
        return True