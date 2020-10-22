

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
        n = len(neighbors)
        
        # Center of kernel
        center = (n // 2, n // 2)
        
        for state in self.patterns.keys():
            count = 0
            for patt in self.patterns[state]:
                for i in range(n):
                    for j in range(n):
                        if (i, j) == center:
                            continue
                        if patt[i][j] not in neighbors[i][j].states:
                            break
                else:
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

            # print('\n'.join(' '.join(t if t is not None else ' ' for t in row) for row in states_combination), '\n')

            if states := self.patterns.get(states_combination):
                return tuple(states)

        neighbor_states_s = '\n'.join(map(str, all_neighbor_states))

        patterns_s = '\n\n'.join(map(
            lambda p: ('\n'.join(' '.join(t if t is not None else ' ' for t in row) for row in p)),
            self.patterns.keys()
        ))
        raise RuntimeError(f"{neighbor_states_s}\ndoesn't match with anything in\n  [\n{patterns_s}\n]")
            

    @staticmethod
    def tuple_neighbors(neighbors):
        """Make an array of neighbors hashable
        by converting it to tuples bottom-up"""
        return tuple(tuple(row) for row in neighbors)