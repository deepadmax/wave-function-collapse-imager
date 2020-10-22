

class Matcher:
    def __init__(self):
        self.patterns = {}

    def add_pattern(self, neighbors, state):
        """Add a state as a possible outcome of certain neighbors"""
        
        neighbors = self.tuple_neighbors(neighbors)
        
        if neighbors not in self.patterns:
            self.patterns[neighbors] = []
        self.patterns[neighbors].append(state)

    def match(self, neighbors):
        """Match a list of neighbors to find possible states"""

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

        for pattern in self.patterns.keys():
            # The number of matching indices within neighbors
            # count = sum(
            #     state in neighbors[i][j].states
            #         for i in range(n)
            #         for j in range(n)
            #     if i != n//2 and j != n//2
            #         for state in pattern[i][j]
            # )

            # Go through every neighbor and count how many states
            # it matches with and how many times it matches with each state
            for i in range(n):
                for j in range(n):
                    if (i, j) == center:
                        continue

                    # Label pattern states and neighbor states more nicely
                    pattern_states = pattern[i][j]
                    # print((i, j), (width, height), [list(map(str, row)) for row in neighbors])
                    neighbor_states = neighbors[i][j].states
                    
                    if pattern_states is not None:
                        # Get which states exist both for the pattern and the neighbor
                        pattern_states_set = set(pattern_states)
                        neighbor_states_set = set(neighbor_states)
                        matching_states = pattern_states_set.intersection(neighbor_states_set)

                        if matching_states:
                            # Loop the matches and add as many as the minimum count
                            # between the pattern and the neighbor
                            states.extend([
                                state * min(
                                    pattern_states.count(state),
                                    neighbor_states.count(state)
                                )
                                for state in matching_states
                            ])
            
        return tuple(states)

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