from src import Field

field = Field.create(
    'demo.pat',
    width=64,
    height=16,
    radius=1
)

field.clear()

# field.seed()

field.collapse()
print(field)