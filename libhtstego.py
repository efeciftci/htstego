import numpy as np
from skimage import io, metrics


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


def fan(I):
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
                if x > 1:
                    I[y + 1, x - 2] = I[y + 1, x - 2] + err * 1 / 16
                if x > 0:
                    I[y + 1, x - 1] = I[y + 1, x - 1] + err * 3 / 16
                I[y + 1, x] = I[y + 1, x] + err * 5 / 16
    return I


def jajuni(I):
    height, width = I.shape
    for y in range(height):
        for x in range(width):
            old_pixel = I[y, x]
            new_pixel = round(I[y, x])
            I[y, x] = new_pixel
            err = old_pixel - new_pixel

            if x + 1 < width:
                I[y, x + 1] = I[y, x + 1] + err * 7 / 48
            if x + 2 < width:
                I[y, x + 2] = I[y, x + 2] + err * 5 / 48

            if y + 1 < height:
                if x - 2 >= 0:
                    I[y + 1, x - 2] = I[y + 1, x - 2] + err * 3 / 48
                if x - 1 >= 0:
                    I[y + 1, x - 1] = I[y + 1, x - 1] + err * 5 / 48
                I[y + 1, x] = I[y + 1, x] + err * 7 / 48
                if x + 1 < width:
                    I[y + 1, x + 1] = I[y + 1, x + 1] + err * 5 / 48
                if x + 2 < width:
                    I[y + 1, x + 2] = I[y + 1, x + 2] + err * 3 / 48

            if y + 2 < height:
                if x - 2 >= 0:
                    I[y + 2, x - 2] = I[y + 2, x - 2] + err * 1 / 48
                if x - 1 >= 0:
                    I[y + 2, x - 1] = I[y + 2, x - 1] + err * 3 / 48
                I[y + 2, x] = I[y + 2, x] + err * 5 / 48
                if x + 1 < width:
                    I[y + 2, x + 1] = I[y + 2, x + 1] + err * 3 / 48
                if x + 2 < width:
                    I[y + 2, x + 2] = I[y + 2, x + 2] + err * 1 / 48

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
    # print(o)
    ps = np.mean(o**2)
    pn = np.mean((o - n)**2)
    return 10 * np.log10(ps / pn)


def htstego_errdiffbin(NSHARES=4,
                       imparam='airplane80',
                       txtparam=512,
                       errdiffmethod='floyd',
                       nooutput=False):
    errdifffun = globals().get(errdiffmethod)
    imfile = f'{imparam}_256gray'
    impath = f'cover_imgs/{imfile}.png'
    I = io.imread(impath, as_gray=True) / 255.0
    M, N = I.shape

    txtfile = f'payloads/payload{txtparam}.txt'
    messageAscii = open(txtfile).read()
    messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)

    blockSize = I.size // len(messageBinary)
    if blockSize == 0:
        print(f'[{NSHARES:2d} {imparam:9s} {txtparam:4d}] message too long!')
        return

    normalOutput = errdifffun(I)  # floyd(I), fan(I)
    stegoOutputs = np.zeros((I.shape[0], I.shape[1], NSHARES))
    linearImage = normalOutput.reshape(1, -1)[0]
    linearStegoImages = np.tile(linearImage, (NSHARES, 1))

    snrs = np.zeros((NSHARES, 2))
    ssims = np.zeros((NSHARES, 1))

    messagePos = 0
    for i in range(0, M * N, blockSize):
        if messagePos < len(messageBinary):
            stegoPixel = int(messageBinary[messagePos])

            if i + blockSize - 1 > M * N:
                print(i + blockSize - 1)
                break

            currentBlock = linearImage[i:i + blockSize]
            stegoBlock = currentBlock.copy()

            embedHere = findEmbedPositionErrDiff(currentBlock, stegoPixel)
            if embedHere == -1:
                continue

            stegoBlock[embedHere] = stegoPixel
            randomShare = np.random.randint(0, NSHARES)
            linearStegoImages[randomShare, i:i + blockSize] = stegoBlock
            messagePos += 1
        else:
            break

    normalOutput = (normalOutput * 255).astype(np.uint8)

    if nooutput == False:
        normalOutputPath = f'output/{imfile}_hterrdiffbin_regular_{errdiffmethod}.png'
        io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        stegoOutputs[:, :, i] = linearStegoImages[i, :].reshape(M, N)
        stegoImage = (stegoOutputs[:, :, i] * 255).astype(np.uint8)
        if nooutput == False:
            stegoOutputPaths.append(
                f'output/{imfile}_hterrdiffbin_stego_msg{txtparam}_{i+1}of{NSHARES}_{errdiffmethod}.png'
            )
            io.imsave(stegoOutputPaths[i], stegoImage)

        snrs[i, 0] = snr(normalOutput, stegoImage)
        snrs[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        ssims[i] = metrics.structural_similarity(stegoImage, normalOutput)

    avg_snr = np.mean(snrs[:, 0])
    avg_psnr = np.mean(snrs[:, 1])
    avg_ssim = np.mean(ssims)
    return avg_snr, avg_psnr, avg_ssim
