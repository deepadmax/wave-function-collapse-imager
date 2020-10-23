import numpy as np
from random import choice
from collections import Counter


class Tile:
    def __init__(self, states):
        self.states = states

    def __str__(self):
        return (self.states[0] if len(self.states) == 1 else ('!' if len(self.states) == 0  else'░'))

    @property
    def has_collapsed(self):
        return len(self.states) < 2

    @property
    def entropy(self):
        entropy = 0
        for state in set(self.states):
            p = self.states.count(state) / len(self.states)
            z = p * np.log(p)
            entropy -= z

        return entropy

    def collapse(self):
        self.states = [Counter(self.states).most_common(1)[0][0]]