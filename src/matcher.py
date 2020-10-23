import numpy as np

class Matcher:
    def __init__(self):
        self.patterns = {}

    def add_pattern(self, neighbors, state):
        """Add a state as a possible outcome of certain neighbors"""

        if state in self.patterns:
            if neighbors not in self.patterns[state]:
                self.patterns[state].append(neighbors)
        else:
            self.patterns[state] = [neighbors]

    def match(self, neighbors):
        """Match a list of neighbors to find possible states"""

        states = []

        # Number of neighbors
        n = len(neighbors)
        
        # Center of kernel
        center = (n // 2)*2
        
        for state in self.patterns.keys():
            count = 0

            for pattern in self.patterns[state]:
                for i, j in np.ndindex((n, n)):
                    if (i, j) != center and pattern[i][j] not in set(neighbors[i][j].states):
                        break
                else:
                    count += 1

            states += [state]*count
            
        return tuple(states)            

    @staticmethod
    def tuple_neighbors(neighbors):
        """Make an array of neighbors hashable
        by converting it to tuples bottom-up"""
        return tuple(tuple(row) for row in neighbors)