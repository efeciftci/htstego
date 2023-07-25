#!/usr/bin/env python3
import argparse
import numpy as np
from skimage import io, metrics
from libhtstego import *

VERSION = '0.0.2'


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

    print(
        f'[erdbin] [{NSHARES:2d} {imparam:10s} {txtparam:4d}] [avg_snr: {avg_snr:.4f}] [avg_psnr: {avg_psnr:.4f}] [avg_ssim: {avg_ssim:.4f}]'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=f'Halftone steganography utility version {VERSION}')
    parser.add_argument('--nshares',
                        type=int,
                        default=4,
                        help='number of output shares to generate (default=4)')
    parser.add_argument('--imparam',
                        type=str,
                        default='airplane80',
                        help='input image (default=airplane80)')
    parser.add_argument('--txtparam',
                        type=int,
                        default=512,
                        help='input payload (default=512)')
    parser.add_argument(
        '--method',
        type=str,
        default='floyd',
        help='error diffusion method (fan, floyd, or jajuni) (default=floyd)')
    parser.add_argument('--no-output',
                        action='store_true',
                        help='do not produce output images (default=false)')
    args = parser.parse_args()
    htstego_errdiffbin(NSHARES=args.nshares,
                       imparam=args.imparam,
                       txtparam=args.txtparam,
                       errdiffmethod=args.method,
                       nooutput=args.no_output)
