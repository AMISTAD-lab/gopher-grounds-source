import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def createDataframe(inputFileNames) -> pd.DataFrame:
    """
    Takes in several files of experiment output and produces one pandas dataframe
    with all files appended together
    """
    dfs = []

    dtypes = {
        'Experiment': 'int',
        'Trap': 'string',
        'Prop_Dead': 'float',
        'Stand_Err': 'float',
        'Conf_Interval': 'string',
        'Intention?': 'bool',
        'Threshold': 'float'
    }

    for inputFile in inputFileNames:
        df: pd.DataFrame = pd.read_csv(inputFile, dtype=dtypes)
        dfs.append(df.drop(columns=['Experiment']))

    df: pd.DataFrame
    for i, frame in enumerate(dfs):
        if (i == 0):
            df = frame
            continue

        df = df.append(frame)

    df.reset_index(drop=True, inplace=True)

    return df

def jitter(arr) -> np.ndarray:
    """
    Takes in an array and introduces jitter into the data points
    """
    stdev = .01 * (max(arr) - min(arr))
    return arr + np.random.randn(len(arr)) * stdev

def createScatterplot(df: pd.DataFrame, x='Fitness', y='Prop_Dead', isJitter=False):
    """
    Takes in a dataframe and creates a scatter plot of y vs x with an optional argument for jitter
    """
    x = np.array(df[x])
    y = np.array(df[y])

    intentionIndices = df.index[df['Intention?'] == True].to_numpy()

    if isJitter:
        x = jitter(x)
        y = jitter(y)

    plt.scatter(x[~intentionIndices], y[~intentionIndices], facecolor='b', edgecolor='b', marker='.', s=30, label='No intention')
    plt.scatter(x[intentionIndices], y[intentionIndices], facecolor='none', edgecolor='r', marker='.', s=30, label='Intention')
    plt.legend(loc='upper right')
    plt.xlabel('Coherence')
    plt.ylabel('Lethality (Proportion of Gophers Dead)')
    plt.title('Lethality vs. Coherence for Coherently Optimized Traps')
    plt.show()
    pass

inputFiles = ['./csv/coherence/coherenceExperimentData.csv']

createScatterplot(createDataframe(inputFiles), isJitter=True)