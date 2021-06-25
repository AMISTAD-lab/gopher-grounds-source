import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.utils as util

## Library functions

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

def addJitter(arr) -> np.ndarray:
    """
    Takes in an array and introduces jitter into the data points
    """
    stdev = .01 * (max(arr) - min(arr))
    return arr + np.random.randn(len(arr)) * stdev

def createScatterplot(df: pd.DataFrame, x='Fitness', y='Prop_Dead', jitter=True, xlabel='', ylabel='', title='', filterIntent=True, labelLoc='upper right'):
    """
    Takes in a dataframe and creates a scatter plot of y vs x with an optional argument for jitter
    """
    x = np.array(df[x])
    y = np.array(df[y])

    intentionIndices = df.index[df['Intention?'] == True].to_numpy()

    if jitter:
        x = addJitter(x)
        y = addJitter(y)

    if filterIntent:
        plt.scatter(x[~intentionIndices], y[~intentionIndices], facecolor='b', edgecolor='b', marker='.', s=30, label='No intention')
        plt.scatter(x[intentionIndices], y[intentionIndices], facecolor='none', edgecolor='r', marker='.', s=30, label='Intention')
        plt.legend(loc = labelLoc)
    else:
        plt.scatter(x, y)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()

inputFiles = ['./csv/functional/functionalExperimentData.csv']

## Plotting functions
def coherenceLethalityVsCoherence():
    """
    Creates a plot of lethality vs coherence for coherently optimized traps
    """
    inputFile = './csv/coherence/coherenceExperimentData.csv'

    df = createDataframe([inputFile])
    createScatterplot(
        df,
        jitter = True,
        xlabel = 'Coherence',
        ylabel = 'Lethality (Proportion of Gophers Dead)',
        title = 'Lethality vs. Coherence for Coherently Optimized Traps'
    )

def functionalCoherenceVsLethality():
    """
    Creates a plot of coherence vs lethality for functionally optimized traps
    """
    inputFile = './csv/functional/functionalExperimentData.csv'

    getCoherenceFromString = \
        lambda strEncoding : functions.coherentFitness(util.convertStringToDecoding(strEncoding))

    df = createDataframe([inputFile])
    
    # Adding the coherence to the dataframe
    df['Coherence'] = df.apply(
        lambda row : getCoherenceFromString(row['Trap']),
        axis = 1
    )

    createScatterplot(
        df,
        x = 'Prop_Dead',
        y = 'Coherence',
        ylabel = 'Coherence',
        xlabel = 'Lethality (Proportion of Gophers Dead)',
        title = 'Coherence vs. Lethality for Functionally Optimized Traps',
        labelLoc = 'upper left'
    )