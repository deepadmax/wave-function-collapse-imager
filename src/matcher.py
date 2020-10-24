import numpy as np

class Matcher:
    def __init__(self):
        self.patterns = {}

    def add_pattern(self, state, neighbor, direction):
        """Add a state as a possible outcome of certain neighbors"""

        if state in self.patterns:
            # if neighbors not in self.patterns[state]:
            if direction in self.patterns[state]:
                self.patterns[state][direction].append(neighbor)
            else:
                self.patterns[state][direction] = [neighbor]
        else:
            self.patterns[state] = {i:[] for i in range(4)}
            self.patterns[state][direction].append(neighbor)

    def match(self, neighbors):
        """Match a list of neighbors to find possible states"""

        states = list(self.patterns.keys())
        
        for i in range(4):
            possible_neighbors = []
            for state in neighbors[i]:
                possible_neighbors += self.patterns[state][(i+2)%4]
            states = [value for value in states if value in possible_neighbors]

        # for i in range(4):
        #     states = [value for value in states if value in neighbors[i]]

        # for state in self.patterns.keys():
        #     count = 0

        #     for i in range(4):
        #         # for patt in self.patterns[state][i]:
        #         #     if patt not in neighbors[i]:
        #         #         do = True
        #         count += len([value for value in self.patterns[state][i] if value in neighbors[i]])
                    
        #     # if do:
        #     #     count += 1
                    

        #     states += [state]*count
            
        return tuple(states)

    @staticmethod
    def tuple_neighbors(neighbors):
        """Make an array of neighbors hashable
        by converting it to tuples bottom-up"""
        return tuple(tuple(row) for row in neighbors)