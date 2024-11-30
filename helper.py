import numpy as np
from PIL import Image

def get_stroke(origin_image, border):
    img = np.asarray(origin_image)
    img_new = np.asarray(Image.new(origin_image.mode, (origin_image.width, origin_image.height), (255, 255, 255, 0))).copy()
    width, height = origin_image.size
    for x in range(width):
        for y in range(height):
            area = img[:, :, 3][x-border:x+border, y-border:y+border]
            if area.shape[0] == 0 or area.shape[1] == 0:
                continue

            img_new[x, y] = (255, 255, 255, area.max() - area.min())
    return Image.fromarray(np.uint8(img_new))