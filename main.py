from src import Field

field = Field()

field.load_from_file('demo.pat')
field.load_patterns()
field.clear()

field.seed()

field.generate()
# print(board)