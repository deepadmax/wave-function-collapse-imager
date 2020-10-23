from src import Field
import time


field = Field.create(
    'demo-2.pat',
    width=32,
    height=16,
    radius=1
)

field.clear()

# field.seed()

start_time = time.time()
if field.collapse():
    print(f'finished! in {(time.time()-start_time)}s.')
    print(field)