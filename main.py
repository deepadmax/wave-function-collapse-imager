from src import Field
import time
from src.image import save_image

field = Field.create_from_file(
    'patterns/demo-1.png',
    width=32,
    height=32,
    N=3,
    transforms=False
)

field.clear()

# field.seed()


start_time = time.time()
if field.collapse():
    print(f'finished! in {(time.time()-start_time)}s')
    # print(field)
    # print(f'Field validation: {"SUCCESSFUL" if field.validate() else "FAILURE"}')
    save_image(field.get_image(),'output/demo-1.png')