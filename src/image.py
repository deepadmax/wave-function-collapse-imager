from PIL import Image

import numpy as np

def read_image(file_name):
    img = Image.open(file_name)

    pixels = np.asarray(img).tolist()

    print(pixels)

    return pixels

def save_image(pixels, file_name):
    img = Image.fromarray(pixels)

    img.save(file_name)