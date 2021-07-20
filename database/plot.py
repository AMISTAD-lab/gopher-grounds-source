import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LogNorm, Normalize, ListedColormap
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import pandas as pd
from progress.bar import IncrementalBar
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
    df = dbLibrary.getTotalCounts(measure)

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
        generations, avgs, marginErrs = dbLibrary.getAverageOptimalFitness(func, step=100)
        plt.plot(generations, avgs, label=func)
        plt.fill_between(generations, avgs + marginErrs, avgs - marginErrs, alpha=0.15)

    plt.title('Cumulative Average Optimal Fitness Across All Trials vs. Generations', pad=20)
    plt.xlabel('Generation')
    plt.ylabel('Average Optimal Fitness value')
    plt.ylim(bottom=-0.05, top=1.05)

    plt.legend()

    if save:
        with PdfPages(f'./images/lineplots/averageOptimalFitness.pdf') as pdf:
            pdf.savefig(bbox_inches='tight')

def createAverageGenerationLinePlot(cumulative=False, start=0, end=10000, step=1, figSize=(6, 6), save=False):
    ''' Creates a line plot which shows the cumulative average fitness across every trial '''
    plt.figure(figsize=figSize)

    generations = None
    labels = ['functional', 'coherence', 'multiobjective']

    for func in labels:
        if cumulative:
            generations, avgs = dbLibrary.getCumulativeAverageFitnessAcrossTrials(func, start, end, step)
        else:
            generations, avgs, marginErrs = dbLibrary.getAverageFitnessAcrossTrials(func, start, end, step)

        plt.plot(generations, avgs, label=func)

        if marginErrs is not None:
            plt.fill_between(generations, avgs + marginErrs, avgs - marginErrs, alpha=0.30)

    plt.title('{}Average Fitness Across All Trials vs. Generations'.format('Cumulative ' if cumulative else ''), pad=20)
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    plt.ylim(top=1)

    plt.legend()

    if save:
        with PdfPages('./images/lineplots/{}GenerationFitness.pdf'.format('cumulative' if cumulative else 'average')) as pdf:
            pdf.savefig(bbox_inches='tight')


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