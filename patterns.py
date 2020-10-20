from cardinals import *


class Pattern:
    def __init__(self, _id, faces=None):
        self.id = _id
        self.faces = faces or [[],[],[],[]]

    def __str__(self):
        return self.id


def load_patterns(fname):
    with open(fname) as f:
        string = f.read().split('\n')
        matrix = [list(line) for line in string]
        return create_patterns(matrix)


def create_patterns(matrix):
    width = len(matrix[0])
    height = len(matrix)

    # Pad matrix with None
    matrix.insert(0, [None]*width)
    matrix.append([None]*width)
    matrix = [[None]+row+[None] for row in matrix]

    patterns = {}

    for y in range(1, len(matrix)-1):
        for x in range(1, len(matrix[y])-1):
            char = matrix[y][x]
            faces = []

            north = matrix[y-1][x]
            east  = matrix[y][x+1]
            south = matrix[y+1][x]
            west  = matrix[y][x-1]

            faces = [north, east, south, west]

            if char is not None and char not in patterns:
                patterns[char] = Pattern(char)

            for d in range(len(faces)):
                if faces[d]:
                    patterns[char].faces[d].append(faces[d])

    return patterns