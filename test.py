from src import Field


field = Field.create(
    'demo.pat',
    width=8,
    height=8,
    N=2
)

field.clear()

i = 0
successes = 0
while True:
    i += 1
    field.clear()

    try:
        field.collapse()

        if field.validate():
            successes += 1
    except RuntimeError:
        pass

    print(f'Success Rate: {((successes / i) * 100):.2f}%, {successes}/{i}{" "*10}', end='\r')