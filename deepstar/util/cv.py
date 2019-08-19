import os

import cv2
import numpy as np


def adjust_color(image_, channel, amount, inc):
    image = image_.copy()

    image = image.astype(np.short)

    t = image[:, :, channel]

    if inc is True:
        t += amount
    else:
        t -= amount

    image[:, :, channel] = t

    image = np.clip(image, 0, 255)

    image = image.astype(np.uint8)

    return image


def alpha_blend(background_, foreground_, mask_):
    background = background_.copy()
    foreground = foreground_.copy()
    mask = mask_.copy()

    background = background.astype(float)
    foreground = foreground.astype(float)
    mask = mask.astype(float) / 255
    foreground = cv2.multiply(mask, foreground)
    background = cv2.multiply(1.0 - mask, background)
    image = cv2.add(foreground, background)

    return image

def overlay_transparent_image(bg, fg, x1, y1):
    # bg is 3 RGB
    # fg is 4 RGBA

    bg = bg.copy()
    fg = fg.copy()

    h, w = fg.shape[:2]
    t = bg[y1:y1 + h, x1:x1 + w]

    b, g, r, a = cv2.split(fg)
    mask = cv2.merge((a, a, a))
    fg = cv2.merge((b, g, r))
    overlaid = alpha_blend(t, fg, mask)

    bg[y1:y1 + h, x1:x1 + w] = overlaid

    return bg
