import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.colors import LogNorm, Normalize

## Library functions
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

## Plotting functions
def create2DHeatmap(df: pd.DataFrame, title='', x_lab='', y_lab='', label_size=12, logScale=True, figIndex=1, figSize=(6,6)):
    ''' Takes in a data frame and optional graph options and creates a heat map from the given data '''
    plt.figure(figIndex, figSize)
    ax = sns.heatmap(df, linewidths=0.5, norm=(LogNorm() if logScale else Normalize()), cmap=sns.cm.rocket_r)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel(x_lab, fontsize=label_size)
    ax.set_ylabel(y_lab, fontsize=label_size)

    return ax

def create1DHeatmap(df: pd.DataFrame, title='', x_lab='', y_lab='Frequency', label_size=12, logScale=True, figIndex=1, figSize=(3,6)):
    ''' Takes in a data frame and optional graph options and creates a one-column vector map from the given data '''
    plt.figure(figIndex, figSize)
    ax = sns.heatmap(df, linewidths=0.5, norm=(LogNorm() if logScale else Normalize()), cmap=sns.cm.rocket_r, square=True)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel(x_lab, fontsize=label_size, labelpad=10)
    ax.set_ylabel(y_lab, fontsize=label_size, labelpad=10)

    pass