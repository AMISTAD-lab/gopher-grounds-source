"""
This file contains all the necessary functions to apply a Simple Good Turing smoothing of a given distribution
"""
import copy
import csv
import numpy as np
import pprint
import database.library as dbLibrary
import geneticAlgorithm.constants as constants

def createFreqOfFreqs(fitnessFunction):
    """
    Returns a dictionary of all frequencies of frequencies of the given input file.
    Additionally, writes the data to a file to prevent having to run the expensive operation again
    """
    inputPath = './frequencies/{}/{}FreqsCompiled.csv'.format(fitnessFunction, fitnessFunction)
    outputPath = './frequencies/{}/{}FreqOfFreqs.csv'.format(fitnessFunction, fitnessFunction)

    # Maintain a dictionary of counts
    freqOfFreqs = {}

    with open(inputPath, 'r') as out:
        reader = csv.reader(out)

        for row in reader:
            if row[1] == 'Freq':
                continue

            currFreq = int(row[1])

            if currFreq not in freqOfFreqs:
                freqOfFreqs[currFreq] = 0
            
            freqOfFreqs[currFreq] += 1
        out.close()

    # Write the data to a file
    with open(outputPath, 'w+') as out:
        writer = csv.writer(out)
        writeData = [['Frequency', 'Frequency_of_Frequency']]
        currI = 1

        copyDict = copy.copy(freqOfFreqs)
        while copyDict:
            if currI in copyDict:
                writeData.append([str(currI), str(copyDict[currI])])
                del copyDict[currI]
            
            currI += 1

        writer.writerows(writeData)
        out.close()

    return freqOfFreqs

def loadFoF(fitnessFunc):
    """
    Returns a dictionary of all frequency of frequencies of a given fitness function
    """
    path = './frequencies/{}/{}FreqOfFreqs.csv'.format(fitnessFunc, fitnessFunc)

    compiledDict = {}
    with open(path, 'r') as out:
        reader = csv.reader(out)

        for row in reader:
            # Skip empty row
            if len(row) == 0:
                continue

            if row[0] == 'Frequency':
                continue

            compiledDict[int(row[0])] = int(row[1])

    return compiledDict

def sgtProbs(fofDict, confidenceLevel=1.65):
    """
    Returns a dictionary mapping the observed frequency to the corresponding smoothed proabilities
    That is, a dictionary {freq: SGTProb}
    """

    N = np.sum([freq * fofDict[freq] for freq in fofDict])
    sortedFreq = sorted(fofDict.keys()) # an array of sorted freqs

    # Compute total probability for objects that has been seen 0 times
    p0 = fofDict[1] / N

    # Compute the dictionary of { r: Z_r }
    Z = computeZ(fofDict, sortedFreq)

    # Compute a linear regression of log(Z[r]) on log(r)
    _, b = logLinearReg(Z)

    # Simple Good Turing
    r_smoothed = {}
    useLinear = False
    for r in sortedFreq:
        r_linear = r * (1 + 1 / r) ** (b + 1)  # estimates of r using LGT

        # If we didn't start use LGT (still using Turing estimate) 
        if not useLinear:
            # 1. if N_r+1==0, switch to LGT
            if (r + 1) not in fofDict:
                # print("reached unobserved frequency before crossing the 'smoothing threshold.'")
                useLinear = True
                r_smoothed[r] = r_linear
                continue

            # 2. if |r_linear - r_turing| <= t, switch to LGT
            Nr = fofDict[r]
            Nrr = fofDict[r + 1]

            t = confidenceLevel * np.sqrt((r + 1) ** 2 * (Nrr / Nr ** 2) * (1 + Nrr / Nr))
            r_turing = (r + 1) * Nrr / Nr # estimates of r using Tuirng estimates

            if abs(r_linear - r_turing) <= t:
                # print("crossed the 'smoothing threshold.'")
                useLinear = True
                r_smoothed[r] = r_linear
                continue
            
            # 3. else, use r_turing
            r_smoothed[r] = r_turing

        # If we started using LGT, continue use it
        if useLinear:
            r_smoothed[r] = r_linear

    # Renormalization
    sgtProb = {}
    sgtProb[0] = p0 / (constants.TOTAL - N)
    unnormTotal = np.sum([r_smoothed[r] * fofDict[r] for r in sortedFreq])
    for r in sortedFreq:
        sgtProb[r] = (1 - p0) * (r_smoothed[r] / unnormTotal)

    return sgtProb

def computeZ(fofDict, sortedFreq):
    """
    Returns a dictionary of {r: Z_r} for every frequency r in sorted order (by r)
    For each r, Z[r] = Z_r = N_r / 0.5(t-q) where q, r, t are successive indices of non-zero fof values
    """
    Z = {}
    for index, r in enumerate(sortedFreq):
        # Find q
        q = sortedFreq[index - 1] if index else 0

        # Find t
        if index == len(sortedFreq) -  1:
            t = 2 * r - q 
        else:
            t = sortedFreq[index + 1]
    
        Z[r] = fofDict[r] / (0.5 * (t - q))

    return Z

def logLinearReg(zDict):
    """ Performs a linear regression on the keys and values of zDict """
    x = np.log(np.fromiter(zDict.keys(), dtype=int))
    y = np.log(np.fromiter(zDict.values(), dtype=float))

    # an nx2 matrix [x^T | 1]
    A = np.vstack([x, np.ones(len(x))]).T   
    b, a = np.linalg.lstsq(A, y, rcond=None)[0]

    # print('Regression: log(z) = {} * log(r) + {}'.format(round(b, 3), round(a, 3)))

    if b > -1.0:
        print('Warning: slope b > -1.0')

    return a, b

def getSmoothedProb(configuration, fitnessFunc, sgtDict):
    """
    Returns the SGT-smoothed probability of a given configuration
    """
    r = dbLibrary.getTrapFreq(configuration, fitnessFunc)
    return sgtDict[r]

def testSGT(configuration, function = 'coherence'):
    # Testing
    fofDict = loadFoF(function)
    sgtTest = sgtProbs(fofDict)

    for key in sgtTest:
        num = int(np.log(sgtTest[key]) / np.log(10))
        sgtTest[key] = round(sgtTest[key], -num + 3)

    print("This is the sgt-smoothed probability dictionary:")

    pprint.pprint(sgtTest)

    print("This is the probability of a certain trap:")
    print(getSmoothedProb(configuration, function, sgtTest))

# testSGT('[48 82 82 43  1 46 48  2 32 67  0 45]', 'functional')