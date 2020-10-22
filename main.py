from src import Field

field = Field.create(
    'demo-1.pat',
    width=128,
    height=8,
    radius=1
)

field.clear()

# field.seed()

field.collapse()
print(field)