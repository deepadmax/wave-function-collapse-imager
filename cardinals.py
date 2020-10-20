NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3

def cardinal_coordinates(x, y):
    return [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]