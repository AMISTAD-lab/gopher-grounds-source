import csv
import os
import pandas as pd
from typing import List

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

def updateCSV(inputPath, data=None, headers = None, overwrite=False):
    '''
    Takes in an input path and a 2D list, then adds the contents of the list to the given input file
    '''
    dirs = inputPath.split('/')

    for i in range(len(dirs)):
        if dirs[i] == '.':
            continue

        if i == len(dirs) - 1:
            break
        
        path = "/".join(dirs[:i + 1])
        if not os.path.exists(path):
            os.mkdir(path)

    if (not os.path.exists(inputPath) and headers) or overwrite:
        with open(inputPath, 'w+', newline='') as out:
            writer = csv.writer(out)
            if headers:
                writer.writerow(headers)
            out.close()

    if data:
        with open(inputPath, 'a', newline='') as out:
            writer = csv.writer(out)
            writer.writerows(data)
            out.close()
