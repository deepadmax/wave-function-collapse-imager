from src import Field

field = Field.create(
    'demo-2.pat',
    width=32,
    height=16,
    radius=2
)

field.clear()

# field.seed()

field.collapse()
print(field)