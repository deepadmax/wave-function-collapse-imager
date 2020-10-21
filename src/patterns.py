from .tiles import Tile

class Pattern:
    def __init__(self):
        self.lib = {}

    def add_pattern(self, char: str, neighbors: list):
        if char in self.lib:
            if neighbors not in self.lib[char]:
                self.lib[char].append(neighbors)
        else:
            self.lib[char] = [neighbors]

    def match(self, neighbors: list):
        # print([tile.pos for row in neighbours for tile in row])

        possible_states = list(self.lib.keys())
        states = []

        N = len(neighbors)

        for state in possible_states:
            count = 0
            state_possible = True
            for patt in self.lib[state]:
                for i in range(N):
                    for j in range(N):
                        if i != N//2 or j != N//2:
                          if patt[i][j] in neighbors[i][j].states:
                              count += 1
                          else:
                              state_possible = False   
                if not state_possible:
                    break
            states = states + [state]*count

        return states