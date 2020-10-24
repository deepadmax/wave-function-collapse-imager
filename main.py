from src import Field
import time


field = Field.create_from_file(
    'patterns/demo-0.pat',
    width=64,
    height=32,
    N=2,
    transforms=False
)

field.clear()

field.seed()


start_time = time.time()
if field.collapse():
    print(f'finished! in {(time.time()-start_time)}s')
    print(field)
    print(f'Field validation: {"SUCCESSFUL" if field.validate() else "FAILURE"}')