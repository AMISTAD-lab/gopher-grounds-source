from typing import List
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize, ListedColormap, LinearSegmentedColormap
from matplotlib.colorbar import ColorbarBase
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from database.constants import FUNC_VALUES
import database.library as dbLibrary

# Defining a color map that has 0 = white
rocketCmap = plt.get_cmap(sns.cm.rocket_r)
rocketWhite = np.vstack([[1, 1, 1, 1], rocketCmap(np.linspace(0.05, 1, 255))])
ROCKET_WHITE_CMAP = ListedColormap(rocketWhite, name='rocket_r_white')

## Helper function
def addJitter(arr: np.ndarray) -> np.ndarray:
    """
    Takes in an array and introduces jitter into the data points
    """
    stdev = .01 * (max(arr) - min(arr))
    return arr + np.random.randn(len(arr)) * stdev

## Plotting functions
def createLethalityCoherenceHeatMap(func: str, log=False, save=False, name='LethalityCoherenceMap'):
    ''' Creates a heat map of the frequency of traps with a certain lethality and coherence '''
    plt.figure()

    if func == 'functional':
        functionName = 'Functionally'
    elif func == 'coherence':
        functionName = 'Coherently'
    elif func == 'multiobjective':
        functionName = 'Multiobjectively'
    elif func == 'random':
        functionName = 'Randomly'
    elif func == 'binary-distance':
        functionName = 'Hamming-Distance'
    elif func == 'uniform-random':
        functionName = 'Uniformly Random'
    else:
        raise Exception(f'{func} is not a valid function name')

    ax = plt.axes([0.15, 0.11, 0.8125, 0.8])
    plt.title(f'Lethality/Coherence Heat Map for {functionName} Optimized Traps')

    # Get data
    data = dbLibrary.getLethalityData(func)

    # Create a heatmap
    sns.heatmap(
        data,
        vmin=0, vmax=1, norm=LogNorm(vmin=1e-7, vmax=1) if log else Normalize(vmin=0, vmax=1),
        cmap=ROCKET_WHITE_CMAP, cbar_kws={ 'label': 'Proportion of traps' },
        ax=ax)
    # ax.set_position([0.075, 0.1, 0.8, 0.825], which='original')
    ax.invert_yaxis()
    ax.set_xlabel('Lethality')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    ax.set_ylabel('Coherence')

    if save:
        with PdfPages('./images/heatmaps/{}{}{}Generated.pdf'.format(func, name, 'Log' if log else '')) as pdf:
            pdf.savefig(bbox_inches='tight')

    return ax

def createVectorMaps(measure: str, figSize=(8,8), save=False, name='VectorMap'):
    '''
    Creates 4 side-by-side heat map vectors of the frequency of traps vs filter applied
    (coherence or lethality).
    '''
    # Get data
    if measure == 'lethality':
        df = dbLibrary.getTotalLethalityCounts()
    elif measure == 'coherence':
        df = dbLibrary.getTotalCoherenceCounts()
    else:
        raise Exception(f'{measure} is not a valid filter')

    # Create figure and subplots
    fig = plt.figure()
    fig.suptitle(f'Proportion of Traps with Given {measure.capitalize()} by Generative Process')

    # Set up axes
    ax = plt.subplot(111)
    fig, axes = plt.subplots(1, len(FUNC_VALUES), sharey=True, num=fig)

    # Turn off the spines and ticks of the big plot
    ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)
    for spine in ('top', 'bottom', 'left', 'right'):    
        ax.spines[spine].set_visible(False)

    # Label the major y label
    ax.set_ylabel('Lethality values' if measure == 'lethality' else 'Coherence values')

    # Adding labels to the major plot
    cbar_ax = plt.axes([.91, .15, .03, .7])

    # Adding heat maps to axes
    for i in range(len(df.columns)):
        currSeries = df.iloc[:, i]

        sns.heatmap(
            currSeries.to_frame(), square=True,
            linecolor='black', rasterized=False, linewidth=1,
            cmap=ROCKET_WHITE_CMAP, cbar=(i == 0), cbar_ax=None if i else cbar_ax,
            yticklabels=True, xticklabels=False,
            ax=axes[i], vmin=0, vmax=1
        )
        plt.setp(axes[i].get_yticklabels(), rotation=0, ha='right', rotation_mode='anchor')

        axes[i].set_title(currSeries.name)
        axes[i].set_ylabel('')
        axes[i].invert_yaxis()
    
    if save:
        with PdfPages(f'./images/vectors/{measure}{name}Generated.pdf') as pdf:
            pdf.savefig(bbox_inches='tight')

def createGenerationBoxPlot(figSize=(9,4), save=False):
    '''
    Creates a box and whisker plot with a categorical y-axis (for each fitness function) and
    the generation on the x-axis. Plots the generation that an optimal trap was found for each experiment.
    '''
    plt.figure(figsize=figSize)
    genMap = {}

    for func in ('functional', 'coherence', 'multiobjective'):
        generationData = dbLibrary.getOptimalGenerations(func)
        genMap[func] = generationData
    
    labels = []
    data = []
    for key in genMap:
        labels.append(key)
        data.append(genMap[key])

    # Set axes configurations
    plt.title('Fitness Function vs. Generation in which Optimal Trap was Found Across Trials')
    plt.xlim(left=-100, right=10100)
    plt.xticks(range(0, 10001, 1000))
    plt.xlabel('Generation')

    plt.boxplot(data, labels=labels, vert=False, flierprops={'marker': 'x', 'markerfacecolor': 'r'})

    if save:
        with PdfPages(f'./images/boxplots/boxplotGeneration.pdf') as pdf:
            pdf.savefig(bbox_inches='tight')

def createAverageOptimalFitnessLinePlot(figSize=(6, 6), save=False):
    ''' Creates a line plot which shows the cumulative average fitness across every trial '''
    plt.figure(figsize=figSize)

    labels = ['functional', 'coherence', 'multiobjective']

    for func in labels:
        generations, avgs = dbLibrary.getAverageOptimalFitness(func, step=100)
        plt.plot(generations, avgs, label=func)

    plt.title('Cumulative Average Optimal Fitness Across All Trials vs. Generations', pad=20)
    plt.xlabel('Generation')
    plt.ylabel('Average Optimal Fitness value')
    plt.ylim(bottom=-0.05, top=1.05)

    plt.legend()

    if save:
        with PdfPages(f'./images/lineplots/averageOptimalFitness.pdf') as pdf:
            pdf.savefig(bbox_inches='tight')

def createAverageGenerationLinePlot(figSize=(6, 6), save=False):
    ''' Creates a line plot which shows the cumulative average fitness across every trial '''
    plt.figure(figsize=figSize)

    generations = None
    labels = ['functional', 'coherence', 'multiobjective']

    for func in labels:
        generations, avgs = dbLibrary.getCumulativeAverage(func)
        plt.plot(generations, avgs, label=func)

    plt.title('Cumulative Average Fitness Across All Trials vs. Generations', pad=20)
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    plt.ylim(top=1)

    plt.legend()

    if save:
        with PdfPages(f'./images/boxplots/averageGenerationFitness.pdf') as pdf:
            pdf.savefig(bbox_inches='tight')