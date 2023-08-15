import json
import os.path
import re
import xml.dom.minidom as minidom
from scipy import stats as st
from skimage import io, metrics
import numpy as np
import settings


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
        if np.sum(np.sum(currentSet[:, 3 * embedHere:3 * embedHere + 3])) != 0 and np.sum(np.sum(currentSet[:, 3 * embedHere:3 * embedHere + 3])) != 9:
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
        outputMatrix = np.zeros((3, sWidth * sHeight * 3, inputMatrix.shape[2]), dtype=inputMatrix.dtype)

    for i in range(sHeight):
        for j in range(sWidth):
            outputMatrix[:, 3 * ((i * sWidth) + j):3 * ((i * sWidth) + j + 1)] = inputMatrix[3 * i:3 * (i + 1), 3 * j:3 * (j + 1)]
    return outputMatrix


def convertHalftoneToMatrix(inputMatrix, sWidth, sHeight):
    if len(inputMatrix.shape) == 2:
        outputMatrix = np.zeros((sHeight * 3, sWidth * 3), dtype=inputMatrix.dtype)
    else:
        outputMatrix = np.zeros((sHeight * 3, sWidth * 3, inputMatrix.shape[2]), dtype=inputMatrix.dtype)

    for i in range(sHeight):
        for j in range(sWidth):
            outputMatrix[3 * i:3 * (i + 1), 3 * j:3 * (j + 1)] = inputMatrix[:, 3 * ((i * sWidth) + j):3 * ((i * sWidth) + j + 1)]
    return outputMatrix


def output_formatter(params, output_format):
    output = ''
    if output_format == 'csv':
        output += ','.join(name for name in params) + '\n'
        output += ','.join(str(value) for value in params.values())
    elif output_format == 'json':
        output += json.dumps(params)
    elif output_format == 'xml':
        md = minidom.Document()
        xml_root = md.createElement('htstegoresult')
        md.appendChild(xml_root)
        for element_name, element_value in params.items():
            xml_element = md.createElement(element_name)
            xml_element.appendChild(md.createTextNode(str(element_value)))
            xml_root.appendChild(xml_element)
        output += md.toxml()

    return output


def htstego_errdiff(NSHARES, coverFile, payloadFile, errdiffmethod, outputMode):
    errdifffun = globals().get(errdiffmethod)

    if outputMode == 'binary':
        I = io.imread(coverFile, as_gray=True)
        I = np.expand_dims(I, axis=-1)
    else:
        I = io.imread(coverFile) / 255.0
    M, N, C = I.shape

    payloadSize = os.path.getsize(payloadFile)
    messageAscii = open(payloadFile).read()
    messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)

    blockSize = M * N // len(messageBinary)
    if blockSize == 0:
        return 'payload too long', 0, 0, 0

    normalOutput = np.zeros((M, N, C))
    linearImage = np.zeros((M * N, C))
    stegoOutputs = np.zeros((NSHARES, M, N, C))
    linearStegoImages = np.zeros((NSHARES, M * N, C))

    for i in range(C):
        normalOutput[:, :, i] = errdifffun(I[:, :, i])
        linearImage[:, i] = normalOutput[:, :, i].reshape(1, -1)[0]
        for j in range(NSHARES):
            linearStegoImages[j, :, i] = linearImage[:, i]

    results = np.zeros((NSHARES, 3))

    messagePos = 0
    for i in range(0, M * N, blockSize):
        if messagePos < len(messageBinary):
            stegoPixel = int(messageBinary[messagePos])

            randomChannel = np.random.randint(C)

            if i + blockSize - 1 > M * N:
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
    if outputMode == 'binary':
        normalOutput = normalOutput[:, :, 0]

    if settings.nofileout == False:
        if not os.path.exists('output'):
            os.makedirs('output')
        imfile = os.path.basename(coverFile).rsplit('.', 1)[0]
        if settings.noregularoutput == False:
            normalOutputPath = f'output/{imfile}_hterrdiff{outputMode[:3]}_regular_{errdiffmethod}.png'
            io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        for j in range(C):
            stegoOutputs[i, :, :, j] = linearStegoImages[i, :, j].reshape(M, N)
        stegoImage = (stegoOutputs[i] * 255).astype(np.uint8)
        if outputMode == 'binary':
            stegoImage = stegoImage[:, :, 0]
        if settings.nofileout == False:
            stegoOutputPaths.append(f'output/{imfile}_hterrdiff{outputMode[:3]}_stego_msg{payloadSize}_{i+1}of{NSHARES}_{errdiffmethod}.png')
            io.imsave(stegoOutputPaths[i], stegoImage)

        cA = None if len(stegoImage.shape) == 2 else 2
        results[i, 0] = snr(normalOutput, stegoImage)
        results[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        results[i, 2] = metrics.structural_similarity(stegoImage, normalOutput, channel_axis=cA)

    avg_snr = np.mean(results[:, 0])
    avg_psnr = np.mean(results[:, 1])
    avg_ssim = np.mean(results[:, 2])
    return 'ok', avg_snr, avg_psnr, avg_ssim


def htstego_pattern(NSHARES, coverFile, payloadFile, outputMode):
    if outputMode == 'binary':
        I = (io.imread(coverFile, as_gray=True) * 255).astype(np.uint8) // 26
        I = np.expand_dims(I, axis=-1)
    else:
        I = io.imread(coverFile) // 26
    M, N, C = I.shape

    payloadSize = os.path.getsize(payloadFile)
    messageAscii = open(payloadFile).read()
    messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)
    messagePos = 1

    normalOutput = np.zeros((M * 3, N * 3, C))
    stegoOutputs = np.zeros((NSHARES, M * 3, N * 3, C))

    nrOfBlocks = M * N
    bwBlocks = countBWBlocks(I)
    nrOfUsableBlocks = nrOfBlocks - bwBlocks
    blockSize = nrOfUsableBlocks // len(messageBinary)
    if blockSize == 0:
        return 'payload too long', 0, 0, 0

    results = np.zeros((NSHARES, 3))
    patMap = np.array([[2, 0, 4], [7, 8, 5], [3, 6, 1]])

    for i in range(NSHARES):
        for j in range(M):
            for k in range(N):
                for l in range(C):
                    p = I[j, k, l]
                    normalOutput[j * 3:(j + 1) * 3, k * 3:(k + 1) * 3, l] = (patMap < p).astype(int)
        stegoOutputs[i] = normalOutput

    linearStegoOutput = np.zeros((NSHARES, 3, M * N * 3, C))
    linearStegoOutput[0] = convertHalftoneToArray(stegoOutputs[0], M, N)
    for i in range(1, NSHARES):
        linearStegoOutput[i] = linearStegoOutput[0]

    for i in range(0, 3 * M * N, 3 * blockSize):
        if messagePos <= len(messageBinary):
            currentBit = messageBinary[messagePos - 1]
            randomChannel = np.random.randint(C)
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
    if outputMode == 'binary':
        normalOutput = normalOutput[:, :, 0]

    if settings.nofileout == False:
        if not os.path.exists('output'):
            os.makedirs('output')
        imfile = os.path.basename(coverFile).rsplit('.', 1)[0]
        if settings.noregularoutput == False:
            normalOutputPath = f'output/{imfile}_htpat{outputMode[:3]}_regular.png'
            io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        stegoImage = (stegoOutputs[i] * 255).astype(np.uint8).copy()
        if outputMode == 'binary':
            stegoImage = stegoImage[:, :, 0]
        if settings.nofileout == False:
            stegoOutputPaths.append(f'output/{imfile}_htpat{outputMode[:3]}_stego_msg{payloadSize}_{i+1}of{NSHARES}.png')
            io.imsave(stegoOutputPaths[i], stegoImage)

        cA = None if len(stegoImage.shape) == 2 else 2
        results[i, 0] = snr(normalOutput, stegoImage)
        results[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        results[i, 2] = metrics.structural_similarity(stegoImage, normalOutput, channel_axis=cA)

    avg_snr = np.mean(results[:, 0])
    avg_psnr = np.mean(results[:, 1])
    avg_ssim = np.mean(results[:, 2])
    return 'ok', avg_snr, avg_psnr, avg_ssim


def htstego_pattern_extract(dirName):
    if not os.path.exists(dirName):
        return

    carrierFiles = [file for file in os.listdir(dirName) if file.endswith('.png')]
    images = []

    for carrier in carrierFiles:
        I = io.imread(f'{dirName}/{carrier}')
        if len(I.shape) == 2:
            I = np.expand_dims(I, axis=-1)
        images.append(I)
    M, N, C = images[0].shape
    
    bitString = ''

    for i in range(0, M, 3):
        for j in range(0, N, 3):
            for k in range(C):
                sums = [np.sum(image[i:i + 3, j:j + 3, k] // 255) for image in images]
                if len(set(sums)) > 1:
                    bitString += '1' if st.mode(sums).mode < np.mean(sums) else '0'

    msg = bytearray()
    for i in range(0, len(bitString), 8):
        msg.append(int(bitString[i:i + 8], 2))
        
    try:
        return bytes(msg).decode('ascii')
    except:
        return 'Cannot extract payload'


def htstego_errdiff_extract(dirName):
    if not os.path.exists(dirName):
        return

    carrierFiles = [file for file in os.listdir(dirName) if file.endswith('.png')]
    images = []
    for carrier in carrierFiles:
        I = io.imread(f'{dirName}/{carrier}')
        if len(I.shape) == 2:
            I = np.expand_dims(I, axis=-1)
        images.append(I)
    M, N, C = images[0].shape

    bitString = ''

    for i in range(M):
        for j in range(N):
            for k in range(C):
                pVal = [image[i, j, k] for image in images]
                if len(set(pVal)) > 1:
                    for v in set(pVal):
                        if pVal.count(v) == 1:
                            bitString += '0' if v == 0 else '1'
                            break

    msg = bytearray()
    for i in range(0, len(bitString), 8):
        msg.append(int(bitString[i:i + 8], 2))
        
    try:
        return bytes(msg).decode('ascii')
    except:
        return 'Cannot extract payload'
