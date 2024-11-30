import numpy as np
from scipy.ndimage import maximum_filter, minimum_filter
from PIL import Image

def get_stroke(origin_image, size):
    img = np.asarray(origin_image).copy()
    img_alpha = img[:, :, 3]
    img_max = maximum_filter(img_alpha, size=size, mode='mirror')
    img_min = minimum_filter(img_alpha, size=size, mode='mirror')
    img[:, :, 0] = 255
    img[:, :, 1] = 255
    img[:, :, 2] = 255
    img[:, :, 3] = img_max - img_min
    return Image.fromarray(np.uint8(img))