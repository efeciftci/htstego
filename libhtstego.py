import numpy as np


def floyd(I):
    height, width = I.shape
    for y in range(height):
        for x in range(width):
            old_pixel = I[y, x]
            new_pixel = np.round(old_pixel)
            I[y, x] = new_pixel

            err = old_pixel - new_pixel

            if x < width - 1:
                I[y, x + 1] += err * 7 / 16
            if y < height - 1:
                if x > 0:
                    I[y + 1, x - 1] += err * 3 / 16
                I[y + 1, x] += err * 5 / 16
                if x < width - 1:
                    I[y + 1, x + 1] += err * 1 / 16
    return I


def findEmbedPositionErrDiff(currentSet, stegoPixel):
    currentSet = np.ravel(currentSet)
    if (stegoPixel == 0
            and np.all(currentSet == 0)) or (stegoPixel == 1
                                             and np.all(currentSet == 1)):
        return -1

    sLen = len(currentSet)
    while True:
        embedHere = np.random.randint(0, sLen)
        if np.any(currentSet[embedHere] != stegoPixel):
            break

    return embedHere


def snr(o, n):
    print(o)
    ps = np.mean(o**2)
    pn = np.mean((o - n)**2)
    return 10 * np.log10(ps / pn)
