import time


cardinal_string: list = ['LEFT', 'DOWN', 'RIGHT', 'UP']

# returns cardinal coordinates relative to ones passed
relative_cardinals = lambda i, j: ((i, j-1), (i-1, j), (i, j+1), (i+1, j))

# [0, 1, 2, 3, 4], n=1 => [1, 2, 3, 4, 0]
# [0, 1, 2, 3, 4], n=2 => [2, 3, 4, 0, 1]
# rotate_list = lambda l, n: l[n:] + l[:n]

# 2D transpose function without using numpy
transpose_2D = lambda l: [[l[j][i] for j in range(len(l))] for i in range(len(l[0]))]

def pattern_compatible(a, b, D):
    """returns true if a and b ovelap in D direction"""

    # just so that they have different values, not that it matters
    A, B = 0, 1

    # LEFT
    if D == 0:
        A = transpose_2D(a)[:-1]
        B = transpose_2D(b)[1:]

    # DOWN
    if D == 1:
        A = a[:-1]
        B = b[1:]

    # RIGHT
    if D == 2:
        A = transpose_2D(a)[1:]#(row[:-1] for row in a)
        B = transpose_2D(b)[:-1]#(row[1:] for row in b)

    # UP
    if D == 3:
        A = a[1:]
        B = b[:-1]
        
    return A == B

# a decorator that prints the time it took a function to execute
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()

        toreturn = func(*args, **kwargs)

        print(f'{func.__name__} took {int((time.time()-start_time)*100)/100}s to finish')

        return toreturn
    
    return wrapper