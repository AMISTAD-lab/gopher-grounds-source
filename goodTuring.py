"""
This file contains all the necessary functions to apply a Simple Good Turing smoothing of a given distribution
"""
import copy
import csv
import numpy as np

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
            if row[0] == 'Frequency':
                continue

            compiledDict[int(row[0])] = int(row[1])

    return compiledDict

def getProbability(configuration, freqDict, fofDict):
    """
    Returns the frequency of a given configuration, the dictionary of frequencies,
    and the dictionary of frequencies of frequencies
    """
    strEncoding = np.array2string(np.array(configuration))
    r = 0 if strEncoding not in freqDict else freqDict[strEncoding]

    r_star = (r + 1) * fofDict[r + 1] / fofDict[r]

    N = np.sum([freq * fofDict[freq] for freq in fofDict])

    return r_star / N

freqDict = loadFrequencies('coherence')
fofDict = loadFoF('coherence')
