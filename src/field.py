import numpy as np

from .matcher import Matcher
from .tile import Tile


class Field:
    def __init__(self, possible_states, matcher, radius=1, width=1, height=1):
        self.possible_states = possible_states
        self.matcher = matcher

        self.radius = radius
        self.width = width
        self.height = height
        
        # Initialize an empty canvas
        self.clear()

    @classmethod
    def create(cls, fname, radius=1, width=10, height=7):
        """Create a canvas from file"""

        with open(fname) as f:
            # A 2D array of characters
            canvas = [list(row) for row in f.read().split('\n')]

            canvas_width = len(canvas[0])
            canvas_height = len(canvas)

            # Make the possible states be the set of all states on the canvas
            possible_states = list(set(
                canvas[i][j]
                for i in range(canvas_height)
                for j in range(canvas_width)
            ))
            
            # Initialize Matcher and add all patterns
            matcher = Matcher()

            # Scan through the canvas and create patterns from each section
            radial_range = range(-radius, radius+1)

            for i in range(height):
                for j in range(width):
                    # An array of neighbors except the center is None
                    neighbors = tuple(
                        tuple(
                            canvas[(i + u) % canvas_height][(j + v) % canvas_width]
                            if u != 0 or v != 0 else None
                            for v in radial_range
                        )
                        for u in radial_range
                    )

                    # for row in neighbors:
                    #     print(' '.join(row))
                    # print()

                    # Get state from center
                    state = canvas[i][j]

                    # Add pattern
                    matcher.add_pattern(neighbors, state)

            return cls(possible_states, matcher, radius, width, height)

    def __str__(self):
        return '\n'.join([''.join([*map(str, row)]) for row in self.canvas])

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
            [Tile((i, j), self.possible_states) for j in range(self.width)]
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
                self.canvas[i][j].entropy if not self.canvas[i][j].has_collapsed else 1000
                for j in range(self.width)
            ]
            for i in range(self.height)
        ])

        # Find the highest entropy
        max_entropy = np.max(entropies)
        entropies[entropies == -1] = max_entropy

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

        radial_range = range(-self.radius, self.radius+1)
        
        neighbors = [
            (
                (i + u) % self.height,
                (j + v) % self.width
            )
            for u in radial_range
            for v in radial_range
            if u != 0 or v != 0
        ]

        return neighbors

    def collapse(self):
        """Until all tiles on the canvas have had their states collapsed,
        continue to propagate the collapse from the tile of lowest entropy
        """

        radial_range = range(-self.radius, self.radius+1)

        while not self.has_collapsed:
            print(self, '\n')
            min_i, min_j = self.get_lowest_entropy()

            self.canvas[min_i][min_j].collapse()

            # Continue until there are no more affected tiles
            affected = self.get_neighbors(min_i, min_j)
            while len(affected) > 0:
                new_affected = []

                # Go through all currently affected tiles
                for i, j in affected:
                    if not self.canvas[i][j].has_collapsed:
                        neighbors = self.get_neighbors(i, j)
                        neighbor_tiles = [
                            [
                                self.canvas[(i + u) % self.height][(j + v) % self.width]
                                for v in radial_range
                            ]
                            for u in radial_range
                        ]

                        # Calculate the new states of (i, j) based on its neighbors
                        new_states = self.matcher.match(neighbor_tiles)

                        # If the new states are different to the current ones,
                        # update the states for (i, j) and add neighbors to affected
                        current_states = self.canvas[i][j].states


                        if tuple(current_states) != new_states:
                            self.canvas[i][j].states = new_states
                            
                            new_affected += [
                                pos for pos in set(neighbors).difference(set(affected))
                                if pos not in new_affected and pos not in affected
                            ]

                affected = []
                if new_affected:
                    affected = new_affected[:]