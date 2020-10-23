import numpy as np
from random import choice, uniform


class Tile:
    def __init__(self, states):
        self.states = states

    def __str__(self):
        return str(self.states[0] if len(self.states) == 1 else ('none' if len(self.states) == 0 else 'multi'))

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

        return entropy + uniform(0,0.01)

    def collapse(self):
        self.states = [choice(self.states)]