import numpy as np
from PIL import Image

def get_stroke(origin_image, border):
    img = np.asarray(origin_image)
    img_alpha = img[:, :, 3]
    img_new = np.asarray(Image.new(origin_image.mode, (origin_image.width, origin_image.height), (255, 255, 255, 0))).copy()
    for x in range(img_alpha.shape[0]):
        for y in range(img_alpha.shape[1]):
            area = img_alpha[x-border:x+border, y-border:y+border]
            if area.shape[0] == 0 or area.shape[1] == 0:
                continue

            img_new[x, y] = (255, 255, 255, area.max() - area.min())
    return Image.fromarray(np.uint8(img_new))