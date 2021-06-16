"""
This file contains all the necessary functions to apply a Simple Good Turing smoothing of a given distribution
"""
import copy
import csv
import pandas as pd

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

createFreqOfFreqs('coherence')