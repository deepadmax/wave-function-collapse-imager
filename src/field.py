import numpy as np

from rich import print

from .matcher import Matcher
from .tile import Tile
from .image import read_image, save_image
from .helper_functions import *


class Field:
    def __init__(self, patterns, matcher, N=1, width=1, height=1, errchar='§'):
        self.patterns = patterns
        self.matcher = matcher

        self.N = N
        self.width = width
        self.height = height

        # The character displayed for tiles which have raised an error
        self.errchar = errchar
        
        # Initialize an empty canvas
        self.clear()

    @classmethod
    def create_from_file(cls, fname, **kwargs):
        """Load a text or image file as a 2D array
        and create a Field from the characters
        """
        if fname.endswith('.png'):
            value_grid = read_image(fname)

            return cls.create(value_grid, **kwargs)
        with open(fname) as f:
            # Turn individual characters into items in a 2D array
            value_grid = [list(row) for row in f.read().split('\n')]

            return cls.create(value_grid, **kwargs)

    @classmethod
    def create(cls, value_grid, N=1, width=10, height=7, symmetry=False):
        """Create a Field from a value grid"""

        # width and height of the value grid
        value_grid_width = len(value_grid[0])
        value_grid_height = len(value_grid)
        
        # Dictionary of patterns used for indexing
        patterns = {}
        # List of patterns used for indexing
        pattern_list = []

        # Looping over every single value
        for i in range(value_grid_height):
            for j in range(value_grid_width):
                # Gather the NxN grid of values for a pattern
                neighbors = tuple(
                    tuple(
                        tuple(value_grid[(i + u) % value_grid_height][(j + v) % value_grid_width])
                        for v in range(N)
                    ) for u in range(N)
                )

                # TODO: implement symmetry
                # Include mirror images and all four different orientations for each
                if symmetry:
                    # The two mirror flips
                    for _flip in range(2):
                        neighbors = tuple(tuple([*map(tuple,row)]) for row in np.fliplr(neighbors))
                        
                        # The four different orientations
                        for _rotate in range(4):
                            neighbors = tuple(tuple([*map(tuple,row)]) for row in np.rot90(neighbors, k=1))

                            if neighbors not in pattern_list:
                                patterns[neighbors] = len(patterns)
                                pattern_list.append(neighbors)
                
                # Do not include all that fancy nonsense and store it plainly
                else:
                    neighbors = tuple(tuple([*map(tuple,row)]) for row in neighbors)

                    if neighbors not in pattern_list:
                        # save_image(np.array(neighbors,dtype='uint8'), f'debug/{len(patterns)}.png')
                        patterns[neighbors] = len(patterns)
                        pattern_list.append(neighbors)

        # Initialize Matcher
        matcher = Matcher()
        rule_count = 0

        for a in pattern_list:
            for b in pattern_list:
                for dir_ind in range(4):
                    if pattern_compatible(a, b, dir_ind):
                        print(f'{patterns[a]} is {cardinal_string[dir_ind]} of {patterns[b]}')
                        matcher.add_pattern(patterns[a], patterns[b], dir_ind)
                        rule_count += 1

        print(f'Loaded {len(patterns)} patterns of size {N}×{N}')
        print(f'There are {rule_count} adjacency rules present')

        # Return a new instance of a Field
        # initialized with the generated parameters
        return cls(pattern_list, matcher, N, width, height)

    def get_image(self, upscale=4):
        """returns a np.ndarray object containing RGBA values for the image"""

        # Make a 2d array with canvas size upscaled
        output = [[0 for i in range(self.width*upscale)] for j in range(self.height*upscale)]
        
        # Loop over the canvas
        for i in range(self.height):
            for j in range(self.width):
                val = 0
                state = self.canvas[i][j].get_state()
                
                if state == 'multi':
                    val = (127,127,127,255)
                elif state == 'none':
                    val = (255,0,0,255)
                else:
                    val = self.patterns[state][0][0]

                for u in range(upscale):
                    for v in range(upscale):
                        output[i*upscale + u][j*upscale + v] = val

        output= tuple([*map(tuple,output)])

        return np.array(output,dtype='uint8')

    def __str__(self):
        output = ""

        # Add top bit of frame
        output += f"┏{'━' * self.width*3}┓\n"

        for row in self.canvas:
            # Add left edge on current row
            output += '┃'

            for tile in row:
                state = tile.get_state()
                
                try:
                    if state == 'multi':
                        output += ' [grey]░░[/grey]'
                    elif state == 'none':
                        output += ' [red]!![/red]'
                    else:
                        output += ' '+str(state).zfill(2)#self.patterns[state][0][0]

                except RuntimeError:
                    output += self.errchar

            # Add right edge on current row
            output += '┃\n'

        # Add bottom bit of frame
        output += f"┗{'━' * self.width*3}┛"

        return output

    @property
    def has_collapsed(self) -> bool:
        """Check if all tiles have had their states collapsed"""
        
        for row in self.canvas:
            for tile in row:
                if not tile.has_collapsed:
                    return False
        return True

    def count_collapsed(self) -> bool:
        """Returns the number of collapsed tiles"""

        count = 0

        for row in self.canvas:
            for tile in row:
                if tile.has_collapsed:
                    count += 1

        return count

    def clear(self):
        """Clear the canvas and set all tiles into superposition"""
        
        self.canvas = [
            [
                Tile(
                    states=list(range(len(self.patterns))) # indices of all the patterns
                ) 
                for j in range(self.width)
            ]
            for i in range(self.height)
        ]

    def seed(self):
        """Collapse the state of a random tile"""
        
        i = np.random.randint(0, self.height)
        j = np.random.randint(0, self.width)
        self.canvas[i][j].collapse()

    # @measure_time
    def get_lowest_entropy(self):
        """Get the index for the lowest entropy tile"""

        # Generate a grid of the entropy for each tile
        entropies = [
            [
                self.canvas[i][j].entropy if not self.canvas[i][j].has_collapsed else 10000000
                for j in range(self.width)
            ]
            for i in range(self.height)
        ]


        # Find the minimum entropy in every row. 
        # basicly a collumn of minimum entropies
        min_collumn = [
            min(row) for row in entropies
        ]

        # get the index of the minimum value in 
        # the minimum collumn.
        i = min_collumn.index(min(min_collumn))
        # now that we know the row in which the 
        # minimum index is located, we can get the
        # index of the minimum value in that row.
        j = entropies[i].index(min(min_collumn))

        # old code
            # # Find the highest entropy
            # max_entropy = np.max(entropies)
            # entropies[entropies == -1] = max_entropy + 1

            # # Find the lowest entropy
            # min_entropy = np.min(entropies)

            # # All the indices which contain the minimum entropy
            # indices = [(int(i), int(j)) for i, j in  zip(*np.where(entropies == min_entropy))]
            
            # # Pick a random element
            # n = np.random.randint(len(indices))
            # i, j = indices[n]

        return (i, j)

    def get_neighbors(self, i, j):
        """Get indices of neighboring tiles at (i, j)"""
        
        neighbors = [
            (
                u % self.height,
                v % self.width
            )
            for u, v in relative_cardinals(i, j)
        ]

        return neighbors

    def collapse(self):
        """Until all tiles on the canvas have had their states collapsed,
        continue to propagate the collapse from the tile of lowest entropy
        """

        while not self.has_collapsed:
            min_i, min_j = self.get_lowest_entropy()

            if not self.canvas[min_i][min_j].has_collapsed:
                self.canvas[min_i][min_j].collapse()

            # Continue until there are no more affected tiles
            affected = self.get_neighbors(min_i, min_j)

            total_updated = 0

            while len(affected) > 0:
                new_affected = []

                # Go through all currently affected tiles
                start_time = time.time()
                for i, j in affected:
                    # print('wowieee!')
                    if not self.canvas[i][j].has_collapsed:
                        neighbors = self.get_neighbors(i, j)
                        neighbor_tiles = [
                            self.canvas[u][v].states
                            for u,v in neighbors
                        ]

                        # Calculate the new states of (i, j) based on its neighbors
                        new_states = self.matcher.match(self.canvas[i][j].states, neighbor_tiles)

                        # If the new states are different to the current ones,
                        # update the states for (i, j) and add neighbors to affected
                        current_states = self.canvas[i][j].states
                        
                        if tuple(current_states) != new_states:
                            # print(new_states)
                            self.canvas[i][j].update_states(new_states)
                            
                            new_affected += [
                                pos for pos in set(neighbors).difference(set(affected))
                                if pos not in new_affected and pos not in affected
                            ]

                            total_updated += 1
                print(time.time()-start_time)

                # if not new_affected:
                #     for i, j in np.ndindex((self.height, self.width)):
                #         if not self.canvas[i][j].has_collapsed:
                #             neighbors = self.get_neighbors(i, j)
                #             neighbor_tiles = [
                #                 self.canvas[u][v].states
                #                 for u,v in neighbors
                #             ]

                #             # Calculate the new states of (i, j) based on its neighbors
                #             new_states = self.matcher.match(self.canvas[i][j].states, neighbor_tiles)

                #             # If the new states are different to the current ones,
                #             # update the states for (i, j) and add neighbors to affected
                #             current_states = self.canvas[i][j].states
                            
                #             if tuple(current_states) != new_states:

                #                 print('ayyy')
                #                 self.canvas[i][j].update_states(new_states)
                                
                #                 new_affected += [
                #                     pos for pos in set(neighbors).difference(set(affected))
                #                     if pos not in new_affected and pos not in affected
                #                 ]

                #                 total_updated += 1

                affected = new_affected
            # print(str(self))
                

            print(f'{int(self.count_collapsed()/(self.width*self.height)*100)}% done')
            print('total updated: ',total_updated)
            # print(str(self).replace('!', "[red]![/red]"), '\n')
        
        # Return False if there are any erroneous tiles
        # if str(self).count(self.errchar):
        #     return False
            # print(str(self))

        return True


    def validate(self):
        """Check whether the generated canvas follows the rules accordingly"""
        
        if not self.has_collapsed:
            self.collapse()

        canvas = np.array(self.canvas)

        for i in range(self.height - self.N):
            for j in range(self.width - self.N):
                # If no patterns can be matched at a particular section,
                # the canvas has not generated a valid configuration
                neighbors = tuple(
                    tuple(
                        self.patterns[canvas[
                            (i + u) % self.height,
                            (j + v) % self.width
                        ].get_state()][0][0]
                        
                        for v in range(self.N)
                    )
                    for u in range(self.N)
                )

                if neighbors not in self.patterns:                        
                    return False
                    
        return True