#!/usr/bin/python3
import numpy as np
from skimage import io, metrics
from libhtstego import floyd, findEmbedPositionErrDiff, snr


def htstego_errdiffbin(NSHARES=4, imparam='airplane80', txtparam=512):
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

    normalOutput = floyd(I)
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
    normalOutputPath = f'output/{imfile}_hterrdiffbin_regular.png'
    io.imsave(normalOutputPath, normalOutput)

    stegoOutputPaths = []
    for i in range(NSHARES):
        stegoOutputs[:, :, i] = linearStegoImages[i, :].reshape(M, N)
        stegoImage = (stegoOutputs[:, :, i] * 255).astype(np.uint8)
        stegoOutputPaths.append(
            f'output/{imfile}_hterrdiffbin_stego_msg{txtparam}_{i+1}of{NSHARES}.png'
        )
        io.imsave(stegoOutputPaths[i], stegoImage)

        snrs[i, 0] = snr(normalOutput, stegoImage)
        snrs[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        ssims[i] = metrics.structural_similarity(stegoImage, normalOutput)

    avg_snr = np.mean(snrs[:, 0])
    avg_psnr = np.mean(snrs[:, 1])
    avg_ssim = np.mean(ssims)

    print(
        f'[erdbin] [{NSHARES:2d} {imparam:10s} {txtparam:4d}] [avg_snr: {avg_snr:.4f}] [avg_psnr: {avg_psnr:.4f}] [avg_ssim: {avg_ssim:.4f}]'
    )


htstego_errdiffbin()
