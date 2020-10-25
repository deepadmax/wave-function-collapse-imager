import numpy as np
from .helper_functions import *

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

    # @measure_time
    def match(self, my_states, neighbors):
        """Match a list of neighbors to find possible states"""

        states = my_states#list(self.patterns.keys())
        
        for i in range(4):
            possible_neighbors = []
            for state in neighbors[i]:
                possible_neighbors += self.patterns[state][(i+2)%4]
            states = [value for value in states if value in possible_neighbors]
            
        return tuple(states)

    @staticmethod
    def tuple_neighbors(neighbors):
        """Make an array of neighbors hashable
        by converting it to tuples bottom-up"""
        return tuple(tuple(row) for row in neighbors)