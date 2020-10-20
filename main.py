from patterns import *
from random import randint as rand
from random import choice
import numpy as np

from patterns import load_patterns
tiles = load_patterns('demo.pat')

from field import Field
field = Field(tiles)

print(field)