"""
This file contains all the necessary functions to apply a Simple Good Turing smoothing of a given distribution
"""
import copy
import csv
import numpy as np
import pprint
import database.library as dbLibrary
import geneticAlgorithm.constants as constants
import geneticAlgorithm.utils as utils

def loadFoF(fitnessFunc):
    """
    Returns a dictionary of all frequency of frequencies of a given fitness function
    """
    return dbLibrary.getFoF(fitnessFunc)

def getProbDict(fofDict, confidenceLevel=1.65):
    """
    Returns a dictionary mapping the observed frequency to the corresponding smoothed proabilities
    That is, a dictionary {freq: SGTProb}
    """
    N = np.sum([freq * fofDict[freq] for freq in fofDict])
    sortedFreq = sorted(fofDict.keys()) # an array of sorted freqs

    if (len(sortedFreq) == 1):
        return { sortedFreq[0]: 1 / constants.TOTAL }

    # Compute total probability for objects that has been seen 0 times
    p0 = fofDict[1] / N

    # Compute the dictionary of { r: Z_r }
    Z = computeZ(fofDict, sortedFreq)

    # Compute a linear regression of log(Z[r]) on log(r)
    _, b = logLinearReg(Z)

    # Simple Good Turing
    r_smoothed = {}
    useLinear = False

    for index, r in enumerate(sortedFreq):
        r_linear = r * (1 + 1 / r) ** (b + 1)  # estimates of r using LGT

        # If we didn't start use LGT (still using Turing estimate) 
        if not useLinear:
            # 1. if N_r+1==0, switch to LGT
            if (r + 1) not in fofDict:
                useLinear = True
                r_smoothed[r] = r_linear
                continue

            # 2. if |r_linear - r_turing| <= t, switch to LGT
            Nr = fofDict[r]
            Nrr = fofDict[r + 1]

            t = confidenceLevel * np.sqrt((r + 1) ** 2 * (Nrr / Nr ** 2) * (1 + Nrr / Nr))
            r_turing = (r + 1) * Nrr / Nr # estimates of r using Tuirng estimates

            if abs(r_linear - r_turing) <= t:
                print("crossed the 'smoothing threshold.'")
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

    # # Test total = 1
    # testTotal = sum([sgtProb[freq] * fofDict[freq] for freq in sortedFreq]) + p0
    # print('test total = ', testTotal)

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

    if b > -1.0:
        raise Exception('Warning: slope b > -1.0')

    return a, b

def getSmoothedProb(configuration, fitnessFunc):
    """
    Returns the SGT-smoothed probability of a given configuration
    """
    probDict = getProbDict(loadFoF(fitnessFunc))

    # # Standardize the trap string
    # trapStr = np.array2string(np.array(configuration))

    r = 0 if dbLibrary.getTrapFreq(configuration, fitnessFunc) == None else dbLibrary.getTrapFreq(configuration, fitnessFunc)
    return probDict[r]

def testSGT(configuration, function = 'coherence'):
    # Testing
    fofDict = loadFoF(function)
    probDict = getProbDict(fofDict)

    for key in probDict:
        num = int(np.log(probDict[key]) / np.log(10))
        probDict[key] = round(probDict[key], -num + 3)

    print("This is the sgt-smoothed probability dictionary:")
    pprint.pprint(probDict)
    print()

    print("This is the probability of a certain trap:")
    print(getSmoothedProb(configuration, function))

testSGT('[ 11, 8, 26, 89, 1, 81, 5, 2, 3, 29, 0, 15 ]', 'coherence')
