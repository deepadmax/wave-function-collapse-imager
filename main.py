from src import *

board = Board()

board.load_from_file('demo.pat')
board.load_patterns()
board.clear()

board.seed()

board.generate()
print(board)