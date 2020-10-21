from random import choice

class Tile:
    def __init__(self, pos: tuple = (0,0), states: list = ['.','#']):
        self.pos = pos
        self.states = states

    @property
    def has_collapsed(self):
        return len(self.states) == 1
    
    def __str__(self):
        return self.states[0] if self.has_collapsed else '░'

    def get_entropy(self):
        return len(self.states)

    def collapse(self):
        self.states = [choice(self.states)]