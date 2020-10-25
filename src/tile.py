import cmath
from random import choice, uniform

from .helper_functions import *

class Tile:
    def __init__(self, states):
        self.states = states

    def get_state(self):
        if len(self.states) == 1:
            return self.states[0]
        elif len(self.states) > 1:
            return 'multi'
        elif len(self.states) == 0:
            return 'none'

    def update_states(self, states):
        # If there's only one type of state,
        # store it simply as a list of one
        if len(set(states)) == 1:
            self.states = [states[0]]

        # Multiple? Store them.
        elif len(self.states) > 1:
            self.states = states

        else:
            raise RuntimeError('No states specified')

    @property
    def has_collapsed(self):
        return len(self.states) == 1

    @property
    def entropy(self):
        p = 1 / len(self.states)
        z = p * cmath.log(p).real
        entropy = -z * len(self.states)
        return entropy + uniform(0,0.01)

    def collapse(self):
        self.states = [choice(self.states)]