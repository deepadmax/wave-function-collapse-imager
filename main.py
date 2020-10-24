from src import Field
import time


field = Field.create_from_file(
    'demo.pat',
    width=32,
    height=16,
    N=2
)

field.clear()

# field.seed()


start_time = time.time()
if field.collapse():
    print(f'finished! in {(time.time()-start_time)}s')
    print(field)
    print(f'Field validation: {"SUCCESSFUL" if field.validate() else "FAILURE"}')