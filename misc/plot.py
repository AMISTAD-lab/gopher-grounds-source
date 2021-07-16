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

def multiobjectivePlot(df: pd.DataFrame, x='functional_fitness', y='coherent_fitness', jitter=False, xlabel='', ylabel='', title='', labelLoc='upper right', box_index=None):
    """
    Plots function vs coherence data from a df. 
    Creates shaded box with upper-right corner at trap with index 'box_index.'
    """
    plt.rcParams.update({'font.size':15})
    fig, ax = plt.subplots()

    x = np.array(df[x])
    y = np.array(df[y])

    if jitter:
        x = addJitter(x)
        y = addJitter(y)

    ax.add_patch(Rectangle((0, 0), x[box_index], y[box_index],
             facecolor = 'gray',
             fill=True,
             lw=1,
             alpha=0.5))
    plt.scatter(x, y, s=100)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()

def barPlot():    
    # creating the dataset
    data = {'random': 0.01, 'functional': 0.01, 'coherent': 1, 'multiobjective': 0.77, 'binary distance': 0.01}
    funcs = list(data.keys())
    diffs = list(data.values())
    
    fig = plt.figure(figsize = (10, 4))
    
    # creating the bar plot
    plt.bar(funcs, diffs, color ='orange',
            width = 0.4)

    addlabels(funcs, diffs)
    
    plt.xlabel("FITNESS FUNCTION")
    plt.ylabel("% DETERMINED MADE WITH INTENTION")
    plt.show()

def addlabels(x,y):
    for i in range(len(x)):
        if y[i] == 0.01:
            plt.text(i,y[i],0,ha='center')
        else:
            plt.text(i,y[i],y[i],ha='center')