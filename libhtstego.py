import numpy as np
from skimage import io, metrics
import os.path, re, settings


def snr(o, n):
    ps = np.mean(o**2)
    pn = np.mean((o - n)**2)
    return 10 * np.log10(ps / pn)


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
                    I[y + 1, x - 2] += err * 1 / 16
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
    if (stegoPixel == 0 and np.all(currentSet == 0)) or (stegoPixel == 1 and np.all(currentSet == 1)):
        return -1

    while True:
        embedHere = np.random.randint(0, len(currentSet))
        if np.any(currentSet[embedHere] != stegoPixel):
            break

    return embedHere


def findEmbedPositionPat(currentSet):
    M, N = currentSet.shape
    if np.sum(np.sum(currentSet)) == 0 or np.sum(np.sum(currentSet)) == M * N:
        return -1

    tol = 0
    while True:
        embedHere = np.random.randint(0, N // 3)
        if np.sum(np.sum(currentSet[:,3 * embedHere:3 * embedHere + 3])) != 0 and np.sum(np.sum(currentSet[:, 3 * embedHere:3 * embedHere + 3])) != 9:
            break
        tol += 1
        if tol == 100:
            embedHere = -1
            break

    return embedHere


def countBWBlocks(I):
    cnt = np.count_nonzero(I == 0) + np.count_nonzero(I == 9)
    return cnt


def convertHalftoneToArray(inputMatrix, sHeight, sWidth):
    if len(inputMatrix.shape) == 2:
        outputMatrix = np.zeros((3, sWidth * sHeight * 3), dtype=inputMatrix.dtype)
    else:
        outputMatrix = np.zeros((3, sWidth * sHeight * 3, 3), dtype=inputMatrix.dtype)

    for i in range(sHeight):
        for j in range(sWidth):
            outputMatrix[:, 3 * ((i * sWidth) + j):3 * ((i * sWidth) + j + 1)] = inputMatrix[3 * i:3 * (i + 1), 3 * j:3 * (j + 1)]
    return outputMatrix


def convertHalftoneToMatrix(inputMatrix, sWidth, sHeight):
    if len(inputMatrix.shape) == 2:
        outputMatrix = np.zeros((sHeight * 3, sWidth * 3), dtype=inputMatrix.dtype)
    else:
        outputMatrix = np.zeros((sHeight * 3, sWidth * 3, 3), dtype=inputMatrix.dtype)

    for i in range(sHeight):
        for j in range(sWidth):
            outputMatrix[3 * i:3 * (i + 1), 3 * j:3 * (j + 1)] = inputMatrix[:, 3 * ((i * sWidth) + j):3 * ((i * sWidth) + j + 1)]
    return outputMatrix


def htstego_errdiffbin(NSHARES, coverFile, payloadFile, errdiffmethod):
    errdifffun = globals().get(errdiffmethod)

    imfile = os.path.splitext(coverFile)[0]
    I = io.imread(f'cover_imgs/{coverFile}', as_gray=True)
    if I.dtype == 'uint8':
        I = I / 255.0
    M, N = I.shape[:2]

    payloadSize = re.search(r'\d+', payloadFile).group()
    messageAscii = open(f'payloads/{payloadFile}').read()
    messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)

    blockSize = M * N // len(messageBinary)
    if blockSize == 0:
        print(f'[{NSHARES:2d} {coverFile:9s} {payloadFile}] message too long!')
        return

    normalOutput = errdifffun(I)
    stegoOutputs = np.zeros((NSHARES, I.shape[0], I.shape[1]))
    linearImage = normalOutput.reshape(1, -1)[0]
    linearStegoImages = np.tile(linearImage, (NSHARES, 1))

    results = np.zeros((NSHARES, 3))

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

    if settings.nofileout == False:
        normalOutputPath = f'output/{imfile}_hterrdiffbin_regular_{errdiffmethod}.png'
        io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        stegoOutputs[i] = linearStegoImages[i, :].reshape(M, N)
        stegoImage = (stegoOutputs[i] * 255).astype(np.uint8)
        if settings.nofileout == False:
            stegoOutputPaths.append(f'output/{imfile}_hterrdiffbin_stego_msg{payloadSize}_{i+1}of{NSHARES}_{errdiffmethod}.png')
            io.imsave(stegoOutputPaths[i], stegoImage)

        results[i, 0] = snr(normalOutput, stegoImage)
        results[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        results[i, 2] = metrics.structural_similarity(stegoImage, normalOutput)

    avg_snr = np.mean(results[:, 0])
    avg_psnr = np.mean(results[:, 1])
    avg_ssim = np.mean(results[:, 2])
    return avg_snr, avg_psnr, avg_ssim


def htstego_errdiffcol(NSHARES, coverFile, payloadFile, errdiffmethod):
    errdifffun = globals().get(errdiffmethod)

    imfile = os.path.splitext(coverFile)[0]
    I = io.imread(f'cover_imgs/{imfile}.png') / 255.0
    M, N = I.shape[:2]

    payloadSize = re.search(r'\d+', payloadFile).group()
    messageAscii = open(f'payloads/{payloadFile}').read()
    messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)

    blockSize = M * N // len(messageBinary)
    if blockSize == 0:
        print(f'[{NSHARES:2d} {coverFile:9s} {payloadFile}] message too long!')
        return

    normalOutput = np.zeros((M, N, 3))
    normalOutput[:, :, 0] = errdifffun(I[:, :, 0])
    normalOutput[:, :, 1] = errdifffun(I[:, :, 1])
    normalOutput[:, :, 2] = errdifffun(I[:, :, 2])

    linearImage = np.zeros((M * N, 3))
    linearImage[:, 0] = normalOutput[:, :, 0].reshape(1, -1)[0]
    linearImage[:, 1] = normalOutput[:, :, 1].reshape(1, -1)[0]
    linearImage[:, 2] = normalOutput[:, :, 2].reshape(1, -1)[0]

    stegoOutputs = np.zeros((NSHARES, M, N, 3))
    linearStegoImages = np.zeros((NSHARES, M * N, 3))
    for i in range(NSHARES):
        linearStegoImages[i, :, 0] = linearImage[:, 0]
        linearStegoImages[i, :, 1] = linearImage[:, 1]
        linearStegoImages[i, :, 2] = linearImage[:, 2]

    results = np.zeros((NSHARES, 3))

    messagePos = 0
    for i in range(0, M * N, blockSize):
        if messagePos < len(messageBinary):
            stegoPixel = int(messageBinary[messagePos])

            randomChannel = np.random.randint(3)

            if i + blockSize - 1 > M * N:
                print('end: ', i + blockSize - 1)
                break

            currentBlock = linearImage[i:i + blockSize, randomChannel]
            stegoBlock = currentBlock.copy()

            embedHere = findEmbedPositionErrDiff(currentBlock, stegoPixel)
            if embedHere == -1:
                continue

            stegoBlock[embedHere] = stegoPixel
            randomShare = np.random.randint(NSHARES)
            linearStegoImages[randomShare, i:i + blockSize, randomChannel] = stegoBlock
            messagePos += 1
        else:
            break

    normalOutput = (normalOutput * 255).astype(np.uint8)

    if settings.nofileout == False:
        normalOutputPath = f'output/{imfile}_hterrdiffcol_regular_{errdiffmethod}.png'
        io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        for j in range(3):
            stegoOutputs[i, :, :, j] = linearStegoImages[i, :, j].reshape(M, N)
        stegoImage = (stegoOutputs[i] * 255).astype(np.uint8)
        if settings.nofileout == False:
            stegoOutputPaths.append(f'output/{imfile}_hterrdiffcol_stego_msg{payloadSize}_{i+1}of{NSHARES}_{errdiffmethod}.png')
            io.imsave(stegoOutputPaths[i], stegoImage)

        results[i, 0] = snr(normalOutput, stegoImage)
        results[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        results[i, 2] = metrics.structural_similarity(stegoImage, normalOutput, channel_axis=2)

    avg_snr = np.mean(results[:, 0])
    avg_psnr = np.mean(results[:, 1])
    avg_ssim = np.mean(results[:, 2])
    return avg_snr, avg_psnr, avg_ssim


def htstego_patbin(NSHARES, coverFile, payloadFile):
    imfile = os.path.splitext(coverFile)[0]
    I = io.imread(f'cover_imgs/{imfile}.png') // 26
    M, N = I.shape[:2]

    payloadSize = re.search(r'\d+', payloadFile).group()
    messageAscii = open(f'payloads/{payloadFile}').read()
    messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)
    messagePos = 1

    normalOutput = np.zeros((M * 3, N * 3))
    stegoOutputs = np.zeros((NSHARES, M * 3, N * 3))

    nrOfBlocks = M * N
    bwBlocks = countBWBlocks(I)
    nrOfUsableBlocks = nrOfBlocks - bwBlocks
    blockSize = nrOfUsableBlocks // len(messageBinary)
    if blockSize == 0:
        print(f'[{NSHARES:2d} {coverFile:9s} {payloadSize:4s}] message too long!')
        return [0, 0, 0]

    results = np.zeros((NSHARES, 3))
    patMap = np.array([[2, 0, 4], [7, 8, 5], [3, 6, 1]])

    for i in range(NSHARES):
        for j in range(M):
            for k in range(N):
                p = I[j, k]
                normalOutput[j * 3:(j + 1) * 3, k * 3:(k + 1) * 3] = (patMap < p).astype(int)
        stegoOutputs[i] = normalOutput

    linearStegoOutput = np.zeros((NSHARES, 3, M * N * 3))
    linearStegoOutput[0] = convertHalftoneToArray(stegoOutputs[0], M, N)
    for i in range(1, NSHARES):
        linearStegoOutput[i] = linearStegoOutput[0]

    for i in range(0, 3 * M * N, 3 * blockSize):
        if messagePos <= len(messageBinary):
            currentBit = messageBinary[messagePos - 1]
            currentSet = linearStegoOutput[0, :, i:i + (3 * blockSize)].copy()

            embedHere = findEmbedPositionPat(currentSet)
            if embedHere == -1:
                continue

            patternHere = np.sum(np.sum(currentSet[:, 3 * embedHere:3 * embedHere + 3])).astype(np.uint8)
            if currentBit == '0':
                newPattern = patternHere - 1
            elif currentBit == '1':
                newPattern = patternHere + 1
            currentSet[:, 3 * embedHere:3 * embedHere + 3] = (patMap < newPattern).astype(int)

            shareToEmbedInto = np.random.randint(NSHARES)
            linearStegoOutput[shareToEmbedInto, :, i:i + (3 * blockSize)] = currentSet.copy()
            messagePos += 1
        else:
            break

    for i in range(NSHARES):
        stegoOutputs[i] = convertHalftoneToMatrix(linearStegoOutput[i], N, M)

    normalOutput = (normalOutput * 255).astype(np.uint8)
    if settings.nofileout == False:
        normalOutputPath = f'output/{imfile}_htpatbin_regular.png'
        io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []
        
    for i in range(NSHARES):
        stegoImage = (stegoOutputs[i] * 255).astype(np.uint8).copy()
        if settings.nofileout == False:
            stegoOutputPaths.append(f'output/{imfile}_htpatbin_stego_msg{payloadSize}_{i+1}of{NSHARES}.png')
            io.imsave(stegoOutputPaths[i], stegoImage)

        results[i, 0] = snr(normalOutput, stegoImage)
        results[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        results[i, 2] = metrics.structural_similarity(stegoImage, normalOutput)

    avg_snr = np.mean(results[:, 0])
    avg_psnr = np.mean(results[:, 1])
    avg_ssim = np.mean(results[:, 2])
    return avg_snr, avg_psnr, avg_ssim


def htstego_patcol(NSHARES, coverFile, payloadFile):
    imfile = os.path.splitext(coverFile)[0]
    I = io.imread(f'cover_imgs/{imfile}.png') // 26
    M, N = I.shape[:2]

    payloadSize = re.search(r'\d+', payloadFile).group()
    messageAscii = open(f'payloads/{payloadFile}').read()
    messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)
    messagePos = 1

    normalOutput = np.zeros((M * 3, N * 3, 3))
    stegoOutputs = np.zeros((NSHARES, M * 3, N * 3, 3))

    nrOfBlocks = M * N
    bwBlocks = countBWBlocks(I)
    nrOfUsableBlocks = nrOfBlocks - bwBlocks
    blockSize = nrOfUsableBlocks // len(messageBinary)
    if blockSize == 0:
        print(f'[{NSHARES:2d} {coverFile:9s} {payloadSize:4s}] message too long!')
        return [0, 0, 0]
    print(f'bwBlocks: {bwBlocks}')
    results = np.zeros((NSHARES, 3))
    patMap = np.array([[2, 0, 4], [7, 8, 5], [3, 6, 1]])

    for i in range(NSHARES):
        for j in range(M):
            for k in range(N):
                for l in range(3):
                    p = I[j, k, l]
                    normalOutput[j * 3:(j + 1) * 3, k * 3:(k + 1) * 3, l] = (patMap < p).astype(int)
            stegoOutputs[i] = normalOutput

    linearStegoOutput = np.zeros((NSHARES, 3, M * N * 3, 3))
    linearStegoOutput[0] = convertHalftoneToArray(stegoOutputs[0], M, N)
    for i in range(1, NSHARES):
        linearStegoOutput[i] = linearStegoOutput[0]

    for i in range(0, 3 * M * N, 3 * blockSize):
        if messagePos <= len(messageBinary):
            currentBit = messageBinary[messagePos - 1]
            randomChannel = np.random.randint(3)
            currentSet = linearStegoOutput[0, :, i:i + (3 * blockSize), randomChannel].copy()

            embedHere = findEmbedPositionPat(currentSet)
            if embedHere == -1:
                continue

            patternHere = np.sum(np.sum(currentSet[:, 3 * embedHere:3 * embedHere + 3])).astype(np.uint8)
            if currentBit == '0':
                newPattern = patternHere - 1
            elif currentBit == '1':
                newPattern = patternHere + 1
            currentSet[:, 3 * embedHere:3 * embedHere + 3] = (patMap < newPattern).astype(int)

            shareToEmbedInto = np.random.randint(NSHARES)
            linearStegoOutput[shareToEmbedInto, :, i:i + (3 * blockSize), randomChannel] = currentSet.copy()
            messagePos += 1
        else:
            break

    for i in range(NSHARES):
        stegoOutputs[i] = convertHalftoneToMatrix(linearStegoOutput[i], N, M)

    normalOutput = (normalOutput * 255).astype(np.uint8)
    if settings.nofileout == False:
        normalOutputPath = f'output/{imfile}_htpatcol_regular.png'
        io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        stegoImage = (stegoOutputs[i] * 255).astype(np.uint8).copy()
        if settings.nofileout == False:
            stegoOutputPaths.append(f'output/{imfile}_htpatcol_stego_msg{payloadSize}_{i+1}of{NSHARES}.png')
            io.imsave(stegoOutputPaths[i], stegoImage)

        results[i, 0] = snr(normalOutput, stegoImage)
        results[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        results[i, 2] = metrics.structural_similarity(stegoImage, normalOutput,channel_axis=2)

    avg_snr = np.mean(results[:, 0])
    avg_psnr = np.mean(results[:, 1])
    avg_ssim = np.mean(results[:, 2])
    return avg_snr, avg_psnr, avg_ssim
