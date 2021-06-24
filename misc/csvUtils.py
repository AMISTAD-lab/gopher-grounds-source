import csv
import os
import pandas as pd
from progress.bar import IncrementalBar
from typing import List
import geneticAlgorithm.encoding as encoding
import geneticAlgorithm.fitnessFunctions as functions

def mergeFreqs(fileNames, fitnessFunction, outputFile):
    """
    Takes in .csv file paths to frequency counts and merges them all into one compiled file
    """
    directory = 'frequencies'
    filePath = './{}/{}/{}.csv'.format(directory, fitnessFunction, outputFile)
    # Read in the CSV as a dataframe to allow for easy manipulation
    dataframes: List[pd.DataFrame] = [
        pd.read_csv('./{}/{}/{}'.format(directory, fitnessFunction, file), index_col = 0)
        for file in fileNames
    ]

    masterDf: pd.DataFrame = None
    for i, df in enumerate(dataframes):
        if i == 0:
            masterDf = df
            continue
        for j, currIndex in enumerate(df.index):
            # Merging all common indices
            if currIndex in masterDf.index:
                masterDf.loc[currIndex].Freq += df.iloc[j]
                df = df.drop(index = currIndex)
        
        # Appending the array afterwards to add all uncommon indices
        masterDf = masterDf.append(df).astype('int32')

    pd.DataFrame.to_csv(masterDf, filePath)

def mergeExperiments(fileNames, fitnessFunction, outputFile):
    """
    Takes in .csv file paths and merges them all into one compiled file
    """
    directory = 'csv'

    filePath = './{}/{}/{}'.format(directory, fitnessFunction, outputFile)
    # Read in the CSV as a dataframe to allow for easy manipulation
    dataframes: List[pd.DataFrame] = [
        pd.read_csv('./{}/{}/{}'.format(directory, fitnessFunction, file), index_col = 0)
        for file in fileNames
    ]

    masterDf: pd.DataFrame = None
    for i, df in enumerate(dataframes):
        if i == 0:
            masterDf = df
            continue
        
        # Appending the new dataframe to compiled one
        masterDf = masterDf.append(df)

    masterDf.reset_index(drop=True, inplace=True)
    masterDf.index.name = 'Experiment'

    pd.DataFrame.to_csv(masterDf, filePath)

def updateCSV(fitness: str, thresholds: None):
    '''
    Takes a list of input CSV files and adds:
        - column for functional fitness
        - column for coherent fitness
        - column for threshold
        - row at the top which contains the number of entries
    '''
    # Create a template with the fitness function pre-populated, and the other variables populated later
    inputPath = './frequencies/{func}/{func}{{}}Thresh{{}}Freqs.csv'.format(func = fitness)
    outputPath = './temps/{func}/{func}{{}}Thresh{{}}Freqs.csv'.format(func = fitness)

    # Define potential thresholds and intentions
    if not thresholds:
        thresholds = (i / 5 for i in range(6))
    
    intentions = ('NoIntention', 'Intention')

    # Create paths if they do not exist
    if not os.path.exists('./temps'):
        os.mkdir('./temps')

    if not os.path.exists('./temps/{}'.format(fitness)):
        os.mkdir('./temps/{}'.format(fitness))

    # Create all pairs of intentions and thresholds if the file exists
    pairs = [
        (intent, thresh)
        for thresh in thresholds
        for intent in intentions
        if os.path.exists(inputPath.format(intent, thresh))
    ]

    tableCounts = []
    numBars = 1000

    # Add row count to the file
    for intent, thresh in pairs:
        with open(inputPath.format(intent, thresh), 'r+') as fileOut:
            with open(outputPath.format(intent, thresh), 'w+') as fileIn:
                fileLines = fileOut.readlines()

                numRows = len(fileLines) - 1
                fileIn.write('{}\n'.format(numRows))

                tableCounts.append(numRows)

                fileIn.close()
                fileOut.close()

    # Takes in a string representation of a list and makes it an encoding
    createEncoding = lambda x: [
        int(digit.strip())
        for digit in x[1:-1].split(' ')
        if digit
    ]

    # Add columns to the file
    for i, (intent, thresh) in enumerate(pairs):
        count = 0
        with IncrementalBar('Processing {} {} thresh {}:\t'.format(fitness, intent.lower(), thresh), max=numBars) as bar:
            with open(inputPath.format(intent, thresh), 'r') as fileOut:
                reader = csv.reader(fileOut)
                with open(outputPath.format(intent, thresh), 'a') as fileIn:
                    writer = csv.writer(fileIn)
                
                    # Reads a row from one file and writes the updated row to a new file
                    for j, row in enumerate(reader):
                        if j == 0:
                            row.extend(['Function', 'Coherence', 'Threshold'])
                            writer.writerow(row)
                            continue
                        
                        # Adding columns
                        trap = createEncoding(row[0])
                        row.append(round(functions.functionalFitness(encoding.singleDecoding(trap)), 4))
                        row.append(round(functions.coherentFitness(encoding.singleDecoding(trap)), 4))
                        row.append(thresh)

                        writer.writerow(row)

                        # Increment the bar 
                        if count % (tableCounts[i] // numBars) == 0:
                            bar.next()

                        count += 1

                    fileIn.close()
                    fileOut.close()

def updateGenerationFile(inputPath, data, headers = None):
    '''
    Takes in an input path and a 2D list, then adds the contents of the list to the given input file
    '''
    if not os.path.exists(inputPath):
        with open(inputPath, 'w+') as out:
            writer = csv.writer(out)
            writer.writerow(headers)

    with open(inputPath, 'a') as out:
        writer = csv.writer(out)
        writer.writerows(data)
