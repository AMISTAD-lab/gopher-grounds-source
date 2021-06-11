import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def createDataframe(inputFileNames) -> pd.DataFrame:
    """
    Takes in several files of experiment output and produces one pandas dataframe
    with all files appended together
    """
    dfs = []
    for inputFile in inputFileNames:
        df: pd.DataFrame = pd.read_csv(inputFile)
        dfs.append(df.drop(columns=['Experiment']))

    df: pd.DataFrame
    for i, frame in enumerate(dfs):
        if (i == 0):
            df = frame
            continue

        df = df.append(frame)

    df.reset_index(drop=True, inplace=True)

    return df

def jitter(arr):
    """
    Takes in an array and introduces jitter into the data points
    """
    stdev = .01 * (max(arr) - min(arr))
    return arr + np.random.randn(len(arr)) * stdev

def createScatterplot(df, x='Fitness', y='Prop_Dead', isJitter=False):
    """
    Takes in a dataframe and creates a scatter plot of y vs x with an optional argument for jitter
    """
    x = df[x]
    y = df[y]

    if isJitter:
        x = jitter(df[x])
        y = jitter(df[y])

    plt.scatter(x, y)
    plt.show()
    pass

threshs = (0.3, 0.5, 0.7)
inputFiles = ['combinedNoIntentionThresh{}.csv'.format(thresh) for thresh in threshs]

createScatterplot(createDataframe(inputFiles))