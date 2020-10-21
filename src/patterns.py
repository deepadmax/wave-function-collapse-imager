from .tiles import Tile

class Pattern:
    def __init__(self):
        self.lib = {}

    def add_pattern(self, char: str, neighbours: list):
        if char in self.lib:
            if neighbours not in self.lib[char]:
                self.lib[char].append(neighbours)
        else:
            self.lib[char] = [neighbours]

    def match(self, neighbours: list):
        print(neighbours)

        possible_states = list(self.lib.keys())
        states = []

        N = len(neighbours)

        for state in possible_states:
            count = 0
            state_possible = True
            for patt in self.lib[state]:
                for i in range(N):
                    for j in range(N):
                        if patt[i][j] in neighbours[i][j].states:
                            count += 1
                        else:
                            state_possible = False   
                if not state_possible:
                    break
            states.append(state*count)

        return states