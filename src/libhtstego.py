#!/usr/bin/env python3

# libhtstego - Halftone Steganography Utility
#
# Copyright (C) 2024 by Efe Çiftci <efeciftci@cankaya.edu.tr>
# Copyright (C) 2024 by Emre Sümer <esumer@baskent.edu.tr>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os
import zlib
import xml.dom.minidom as minidom
from datetime import datetime
from fractions import Fraction
from scipy import stats as st
from skimage import io, metrics
import numpy as np
import settings


def snr(o, n):
    ps = np.mean(o**2)
    pn = np.mean((o - n)**2)
    return 10 * np.log10(ps / pn)


def get_kernel_list():
    kernel_list = []
    for file in os.listdir('kernels'):
        if file.endswith('.txt'):
            kernel_list.append(os.path.splitext(file)[0])
    return kernel_list


def applyErrDiff(I, kernelFile):
    with open(f'kernels/{kernelFile}.txt', 'r') as file:
        lines = file.readlines()
        kernel = [[float(Fraction(value)) if value != 'X' else 0 for value in line.split()] for line in lines]
    kernel = np.array(kernel)
    kH, kW = kernel.shape

    height, width = I.shape
    pI = kW // 2
    tI = np.zeros((height + pI*2, width + pI*2))
    tI[pI:-pI, pI:-pI] = I

    for y in range(height):
        for x in range(width):
            old_pixel = tI[y+pI, x+pI]
            new_pixel = np.round(old_pixel)
            tI[y+pI, x+pI] = new_pixel
            err = old_pixel - new_pixel
            tI[y:y+kH, x:x+kW] += err * kernel
            
    return tI[pI:-pI, pI:-pI]


def generateBayerMatrix(n):
    if n == 1:
        return np.array([[0]])
    m = 4 * n * n * generateBayerMatrix(n / 2)
    top = np.hstack((m, m + 3))
    bottom = np.hstack((m + 2, m + 1))
    return np.vstack((top, bottom)) / (4 * n * n)


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


def generateOutputDirectory():
    if not os.path.exists('output'):
        os.makedirs('output')

    currentDateTime = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    outputDirs = [d for d in os.listdir('output') if d.startswith(currentDateTime)]
    if outputDirs:
        lastDir = sorted(outputDirs, key=lambda x: int(x.split('-')[-1]))[-1]
        lastNum = int(lastDir.split('-')[-1])
        print(lastNum)
        dirName = f'{currentDateTime}-{lastNum+1}'
    else:
        dirName = f'{currentDateTime}-0'

    os.makedirs(f'output/{dirName}')
    return f'output/{dirName}'

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


def htstego_errdiff(NSHARES, coverFile, payloadFile, errDiffMethod, outputMode):
    if outputMode == 'binary':
        I = io.imread(coverFile, as_gray=True)
        I = np.expand_dims(I, axis=-1)
    else:
        I = io.imread(coverFile) / 255.0

    if outputMode == 'color' and len(I.shape) < 3:
        return 'cannot generate color output from grayscale input', 0, 0, 0

    M, N, C = I.shape

    payloadSize = os.path.getsize(payloadFile)
    messageAscii = open(payloadFile).read()
    if settings.compress:
        messageAscii = zlib.compress(bytes(messageAscii.encode('utf-8')))
        messageBinary = ''.join(format(ord(chr(c)), '08b') for c in messageAscii)
    else:
        messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)

    blockSize = M * N // len(messageBinary)
    if blockSize == 0:
        return 'payload too long', 0, 0, 0

    normalOutput = np.zeros((M, N, C))
    linearImage = np.zeros((M * N, C))
    stegoOutputs = np.zeros((NSHARES, M, N, C))
    linearStegoImages = np.zeros((NSHARES, M * N, C))

    for i in range(C):
        normalOutput[:, :, i] = applyErrDiff(I[:, :, i], errDiffMethod)
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
        outDir = generateOutputDirectory()
        imfile = os.path.basename(coverFile).rsplit('.', 1)[0]
        if settings.regularoutput == True:
            normalOutputPath = f'{outDir}/{imfile}_hterrdiff{outputMode[:3]}_regular_{errDiffMethod}.png'
            io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        for j in range(C):
            stegoOutputs[i, :, :, j] = linearStegoImages[i, :, j].reshape(M, N)
        stegoImage = (stegoOutputs[i] * 255).astype(np.uint8)
        if outputMode == 'binary':
            stegoImage = stegoImage[:, :, 0]
        if settings.nofileout == False:
            stegoOutputPaths.append(f'{outDir}/{imfile}_hterrdiff{outputMode[:3]}_stego_msg{payloadSize}_{i+1}of{NSHARES}_{errDiffMethod}.png')
            io.imsave(stegoOutputPaths[i], stegoImage)

        cA = None if len(stegoImage.shape) == 2 else 2
        results[i, 0] = snr(normalOutput, stegoImage)
        results[i, 1] = metrics.peak_signal_noise_ratio(stegoImage, normalOutput)
        results[i, 2] = metrics.structural_similarity(stegoImage, normalOutput, channel_axis=cA)

    avg_snr = np.mean(results[:, 0])
    avg_psnr = np.mean(results[:, 1])
    avg_ssim = np.mean(results[:, 2])
    return 'ok', avg_snr, avg_psnr, avg_ssim


def htstego_ordered(NSHARES, coverFile, payloadFile, bayerN, outputMode):
    if outputMode == 'binary':
        I = io.imread(coverFile, as_gray=True)
        I = np.expand_dims(I, axis=-1)
    else:
        I = io.imread(coverFile) / 255.0

    if outputMode == 'color' and len(I.shape) < 3:
        return 'cannot generate color output from grayscale input', 0, 0, 0

    M, N, C = I.shape

    payloadSize = os.path.getsize(payloadFile)
    messageAscii = open(payloadFile).read()
    if settings.compress:
        messageAscii = zlib.compress(bytes(messageAscii.encode('utf-8')))
        messageBinary = ''.join(format(ord(chr(c)), '08b') for c in messageAscii)
    else:
        messageBinary = ''.join(format(ord(c), '08b') for c in messageAscii)

    blockSize = M * N // len(messageBinary)
    if blockSize == 0:
        return 'payload too long', 0, 0, 0

    normalOutput = np.zeros((M, N, C), dtype=np.uint8)
    stegoOutputs = np.zeros((NSHARES, M, N, C), dtype=np.uint8)
    results = np.zeros((NSHARES, 3))

    bM = np.multiply(generateBayerMatrix(bayerN), 4)
    bitIndex = 0
    randPos = np.random.randint(0, NSHARES)

    for y in range(M):
        for x in range(N):
            cP = N * y + x
            threshold = bM[x % bayerN][y % bayerN]
            for z in range(C):
                newPixel = 255 if I[y, x, z] > threshold else 0
                normalOutput[y, x, z] = newPixel
                stegoOutputs[:, y, x, z] = newPixel

            if bitIndex < len(messageBinary):
                if cP % blockSize == randPos and cP // blockSize == bitIndex:
                    sP = 255 if messageBinary[bitIndex] == '1' else 0
                    rC = np.random.randint(0, C)
                    rO = np.random.randint(0, NSHARES)
                    stegoOutputs[:, y, x, rC] = np.where(np.arange(NSHARES) == rO, sP, 255 - sP)
                    bitIndex += 1
                    randPos = np.random.randint(0, blockSize)

    if outputMode == 'binary':
        normalOutput = normalOutput[:, :, 0]

    if settings.nofileout == False:
        outDir = generateOutputDirectory()
        imfile = os.path.basename(coverFile).rsplit('.', 1)[0]
        if settings.regularoutput == True:
            normalOutputPath = f'{outDir}/{imfile}_htordered{outputMode[:3]}_regular_bayer{bayerN}.png'
            io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        stegoImage = stegoOutputs[i]
        if outputMode == 'binary':
            stegoImage = stegoImage[:, :, 0]
        if settings.nofileout == False:
            stegoOutputPaths.append(f'{outDir}/{imfile}_htordered{outputMode[:3]}_stego_msg{payloadSize}_{i+1}of{NSHARES}_bayer{bayerN}.png')
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
    if settings.compress:
        messageAscii = zlib.compress(bytes(messageAscii.encode('utf-8')))
        messageBinary = ''.join(format(ord(chr(c)), '08b') for c in messageAscii)
    else:
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
        outDir = generateOutputDirectory()
        imfile = os.path.basename(coverFile).rsplit('.', 1)[0]
        if settings.regularoutput == True:
            normalOutputPath = f'{outDir}/{imfile}_htpat{outputMode[:3]}_regular.png'
            io.imsave(normalOutputPath, normalOutput)
        stegoOutputPaths = []

    for i in range(NSHARES):
        stegoImage = (stegoOutputs[i] * 255).astype(np.uint8).copy()
        if outputMode == 'binary':
            stegoImage = stegoImage[:, :, 0]
        if settings.nofileout == False:
            stegoOutputPaths.append(f'{outDir}/{imfile}_htpat{outputMode[:3]}_stego_msg{payloadSize}_{i+1}of{NSHARES}.png')
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
        return zlib.decompress(bytes(msg)).decode('ascii')
    except zlib.error:
        try:
            return bytes(msg).decode('ascii')
        except:
            return 'Cannot extract payload'
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
        return zlib.decompress(bytes(msg)).decode('ascii')
    except zlib.error:
        try:
            return bytes(msg).decode('ascii')
        except:
            return 'Cannot extract payload'
    except:
        return 'Cannot extract payload'


def htstego_ordered_extract(dirName):
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

    for y in range(M):
        for x in range(N):
            for k in range(C):
                pVal = [image[y, x, k] for image in images]
                if len(set(pVal)) > 1:
                    for v in set(pVal):
                        if pVal.count(v) == 1:
                            bitString += '0' if v == 0 else '1'
                            break

    msg = bytearray()
    for i in range(0, len(bitString), 8):
        msg.append(int(bitString[i:i + 8], 2))

    try:
        return zlib.decompress(bytes(msg)).decode('ascii')
    except zlib.error:
        try:
            return bytes(msg).decode('ascii')
        except:
            return 'Cannot extract payload'
    except:
        return 'Cannot extract payload'
