from patterns import load_patterns
tiles = load_patterns('demo.pat')

from field import Field
field = Field(tiles)

field.collapse()
print(field)