from typing import List
import pandas as pd

def mergeCSVFiles(fileNames, fitnessFunction, outputFile, frequencies=True):
    """
    Takes in .csv file paths and merges them all into one compiled file
    """
    directory = 'frequencies'
    if not frequencies:
        directory = 'csv'

    filePath = './{}/{}/{}.csv'.format(directory, fitnessFunction, fitnessFunction, outputFile)
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