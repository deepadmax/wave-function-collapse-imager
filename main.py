from src import Field

field = Field.create(
    'demo.pat',
    width=32,
    height=9
)

field.clear()

# field.seed()

field.collapse()
print(field)