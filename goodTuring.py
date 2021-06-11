"""
This file contains all the necessary functions to apply a Simple Good Turing smoothing of a given distribution
"""
import copy
import csv
import pandas as pd
import time

def createFreqOfFreqs(fitnessFunction):
    """
    Returns a dictionary of all frequencies of frequencies of the given input file.
    Additionally, writes the data to a file to prevent having to run the expensive operation again
    """
    inputPath = './frequencies/{}/{}FreqsCompiled.csv'.format(fitnessFunction, fitnessFunction)
    outputPath = './frequencies/{}/{}FreqOfFreqs.csv'.format(fitnessFunction, fitnessFunction)

    # Read in the file to count
    df = pd.read_csv(inputPath, index_col=0, dtype={'Trap': 'string', 'Freq': 'Int32'})
    
    # Maintain a dictionary of counts
    freqOfFreqs = {}

    # Count the frequency of all the frequencies
    for i in range(len(df.index)):
        if i == 0:
            continue

        currFreq = df.iloc[i].Freq
        if currFreq not in freqOfFreqs:
            freqOfFreqs[currFreq] = 0
        
        freqOfFreqs[currFreq] += 1

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

createFreqOfFreqs('random')