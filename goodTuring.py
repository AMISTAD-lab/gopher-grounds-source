"""
This file contains all the necessary functions to apply a Simple Good Turing smoothing of a given distribution
"""
import copy
import csv
import numpy as np
from numpy.core.fromnumeric import sort
from scipy import linalg

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

def SGTProbs(freqDict, fofDict, confidenceLevel=1.96):
    """
    Returns a dictionary mapping the observed frequency to the corresponding smoothed proabilities
    That is, a dictionary {freq: SGTProb}
    """
    probDict = {}
    N = np.sum([freq * fofDict[freq] for freq in fofDict])
    sortedFreq = sorted(fofDict.keys()) #a array of sorted freqs
    print(N == sum(freqDict.values()))

    probDict[0] = fofDict[1] / N

    # Compute the dictionary of {r: Z_r}
    Z = computeZ(fofDict, sortedFreq)

     # Compute a linear regression of log(Z[r]) on log(r)
    a, b = logLinearReg(Z)

    # Simple Good Turing
    rSmoothed = {}
    useLinear = False
    for r in sortedFreq:
        r_linear = r * (1 + 1/r)^(b + 1) 

        # If we started using LGT, continue use it

        # If we didn't start use LGT (still using Turing estimate), check 1.the difference between two estimates, 2.if N_r+1==0, switch to LGT
    pass

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
            t = r + (r - q)        # Not sure what this should be
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


freqDict = loadFrequencies('coherence')
print("finish loading freqDict")
print()
fofDict = loadFoF('coherence')
sortedFreq = sorted(fofDict.keys())
Z = computeZ(fofDict, sortedFreq)
logLinearReg(Z)

