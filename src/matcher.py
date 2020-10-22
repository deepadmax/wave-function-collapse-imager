

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
        N = len(neighbors)
        n = N//2
        
        for state in self.patterns.keys():
            count = 0
            for patt in self.patterns[state]:
                possible = True
                for i in range(N):
                    for j in range(N):
                        if i == n and j == n:
                            continue

                        if patt[i][j] not in neighbors[i][j].states:
                            possible = False   

                if possible:
                    count += 1

            states += [state]*count
            
        return states
    
    def exact_match(self, neighbors):
        """This is a modified version of Matcher.match,
        which allows only exact matches with neighbors"""

        states = []
        # Number of neighbors
        n = len(neighbors)
        
        # Neighborhood width & height
        width = len(neighbors[0])
        height = len(neighbors)

        # Half way through the list
        half_way = n // 2
        # And its center coordinates
        center = (half_way, half_way)

        neighbors = self.tuple_neighbors(neighbors)

        # [[1 2] [4 5 6]]
        # ([1] + y for y in ([4] + z for z in ()))
        def combinations(l):
            if len(l) == 1:
                yield from ([x] for x in l[0])

            else:
                for x in l[0]:
                   for y in combinations(l[1:]):
                        yield [x] + y

        all_neighbor_states = [
            neighbors[i][j].states
            for i in range(n)
            for j in range(n)
        ]

        latest_comb = None
        for states_combination in combinations(all_neighbor_states):
            states_combination = [
                [
                    states_combination[i*n+j]
                    for j in range(n)
                ]
                for i in range(n)
            ]

            states_combination[half_way][half_way] = None
            states_combination = self.tuple_neighbors(states_combination)

            if states_combination[0][:2] != latest_comb:
                print(latest_comb)
                latest_comb = states_combination[0][:2]

            if states := self.patterns.get(states_combination):
                return tuple(states)

        all_patterns = '\n  '.join(map(str, self.patterns.keys()))
        raise RuntimeError(f"{all_neighbor_states}\ndoesn't match with anything in\n  [\n{all_patterns}\n]")
            

    @staticmethod
    def tuple_neighbors(neighbors):
        """Make an array of neighbors hashable
        by converting it to tuples bottom-up"""
        return tuple(tuple(row) for row in neighbors)