"""
This file contains all the necessary functions to apply a Simple Good Turing smoothing of a given distribution
"""
import copy
import csv
import numpy as np
from numpy.core.fromnumeric import sort
from scipy import linalg

# Define constant necessary for computing the smoothed probability
TOTAL = 427929800129788411

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

def loadFrequencies(fitnessFunc):
    """
    Returns a dictionary of { 'strEncoding': frequency } of all frequencies of a given fitness function
    """
    outputPath = './frequencies/{}/{}FreqsCompiled.csv'.format(fitnessFunc, fitnessFunc)

    compiledDict = {}
    with open(outputPath, 'r') as out:
        reader = csv.reader(out)

        for row in reader:
            if row[1] == 'Freq':
                continue

            if row[0] in compiledDict:
                raise Exception('Duplicate trap {}'.format(row[0]))
            
            compiledDict[row[0]] = int(row[1])
    
    return compiledDict

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

def turingProb(configuration, freqDict, fofDict):
    """
    Returns the frequency of a given configuration, the dictionary of frequencies,
    and the dictionary of frequencies of frequencies
    """
    strEncoding = np.array2string(np.array(configuration))
    r = 0 if strEncoding not in freqDict else freqDict[strEncoding]

    r_star = (r + 1) * fofDict[r + 1] / fofDict[r]

    N = np.sum([freq * fofDict[freq] for freq in fofDict])

    return r_star / N

def sgtProbs(fofDict, confidenceLevel=1.65):
    """
    Returns a dictionary mapping the observed frequency to the corresponding smoothed proabilities
    That is, a dictionary {freq: SGTProb}
    """

    N = np.sum([freq * fofDict[freq] for freq in fofDict])
    sortedFreq = sorted(fofDict.keys()) #a array of sorted freqs
    # print(N == sum(freqDict.values()))

    # Compute total probability for objects that has been seen 0 times
    p0 = fofDict[1] / N

    # Compute the dictionary of {r: Z_r}
    Z = computeZ(fofDict, sortedFreq)

    # Compute a linear regression of log(Z[r]) on log(r)
    a, b = logLinearReg(Z)

    # Simple Good Turing
    r_smoothed = {}
    useLinear = False
    for r in sortedFreq:
        r_linear = r * (1 + 1/r)**(b + 1)  # estimates of r using LGT

        # If we didn't start use LGT (still using Turing estimate) 
        if not useLinear:
            # 1. if N_r+1==0, switch to LGT (!!!Not sure if we have this)
            if r+1 not in fofDict:
                print("reached unobserved frequency before crossing the 'smoothing threshold.'")
                useLinear = True
                r_smoothed[r] = r_linear
                continue
            # 2. if |r_linear - r_turing| <= t, switch to LGT
            t = confidenceLevel * np.sqrt((r+1)**2 * (fofDict[r+1] / fofDict[r]**2) * (1 + fofDict[r+1]/fofDict[r]))
            r_turing = (r + 1) * fofDict[r + 1] / fofDict[r] # estimates of r using Tuirng estimates
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
    sgtProb[0] = p0 / (TOTAL - N)
    unnormTotal = np.sum([r_smoothed[r] * fofDict[r] for r in sortedFreq])
    for r in sortedFreq:
        sgtProb[r] = (1 - p0) * (r_smoothed[r] / unnormTotal)

    # checkTotal = np.sum([sgtProb[r] * fofDict[r] for r in sortedFreq]) + p0
    # print(checkTotal)

    return sgtProb

def computeZ(fofDict, sortedFreq):
    """
    Returns a dictionary of {r: Z_r} for every frequency r in sorted order (by r)
    For each r, Z[r] = Z_r = N_r / 0.5(t-q) where q, r, t are successive indices of non-zero fof values
    """
    Z = {}
    for index, r in enumerate(sortedFreq):
        # Find q
        if index == 0:
            q = 0
        else:
            q = sortedFreq[index - 1]
        # Find t
        if index == len(sortedFreq) -  1:
            t = 2 * r -q 
        else:
            t = sortedFreq[index + 1]
    
        Z[r] = fofDict[r] / (0.5 * (t - q))
    return Z

def logLinearReg(zDict):
    x = np.log(np.fromiter(zDict.keys(), dtype=int))
    y = np.log(np.fromiter(zDict.values(), dtype=float))
    A = np.vstack([x, np.ones(len(x))]).T
    b, a = np.linalg.lstsq(A, y, rcond=None)[0]
    print('Regression: log(z) = {b}*log(r) + {a}'.format(b = b, a = a))
    if b > -1.0:
        print('Warning: slope b > -1.0')
    return a, b

def getSmoothedProb(configuration, freqDict, sgtDict):
    """
    Returns the SGT-smoothed probability of a given configuration
    """
    strEncoding = np.array2string(np.array(configuration))
    r = 0 if strEncoding not in freqDict else freqDict[strEncoding]
    return sgtDict[r]

#Testing
freqDict = loadFrequencies('coherence')
fofDict = loadFoF('coherence')
sortedFreq = sorted(fofDict.keys())

sgtTest = sgtProbs(fofDict)
print("This is the sgt-smoothed probability dictionary:")
print(sgtTest)
print("This is the probability of a certain trap:")
print(getSmoothedProb([11, 43, 13,  5,  1, 40, 77,  2, 33, 31,  0, 15], freqDict, sgtTest))

