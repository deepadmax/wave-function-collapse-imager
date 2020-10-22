from random import choice


class Tile:
    def __init__(self, pos, states):
        self.pos = pos
        self.states = states

    def __str__(self):
        return self.states[0] if self.has_collapsed else '░'

    @property
    def has_collapsed(self):
        return self.entropy == 1

    @property
    def entropy(self):
        return len(self.states)

    def collapse(self):
        self.states = [choice(self.states)]