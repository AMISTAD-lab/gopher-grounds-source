import csv
import copy
import pandas as pd
import matplotlib.pyplot as plt
import statistics as stats
import math as m
import geneticAlgorithm.constants as constants




def statusOverTime(filename, fitnessFunc):
    """displays a graph with information about the lifes of intention and normal gophers"""

    data = pd.read_csv(filename)
    plt.style.use('ggplot')
    # plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
        
    df0 = filterDataFrame(data, [["intention", 0]])
    df1 = filterDataFrame(data, [["intention", 1]])

    dfs = [df0, df1]
    modes = [r"Without Intention", r"With Intention"]

    figs = []
    axes = []
    for i in range(2):
        figs.append(plt.figure(i + 1))
        axes.append(plt.gca())

        x = [t for t in range(0, 50+1)]
        alive = [0]*51
        starved = [0]*51
        zapped = [0]*51

        for _, gopher in dfs[i].iterrows():
            numTraps = int(gopher["numTraps"])
            status = int(gopher["status"])
            for j in range(numTraps+1):
                alive[j] += 1
            if status != 0:
                if status == 1:
                    dead_list = starved
                else:
                    dead_list = zapped
                for j in range(numTraps+1, 50 + 1):
                    dead_list[j] += 1

        total = alive[0] + starved[0] + zapped[0]
        alive = [a / total * 100 for a in alive]
        starved = [s / total * 100 for s in starved]
        zapped = [z / total * 100 for z in zapped]
        print(alive[-1])
        print(starved[-1])
        print(zapped[-1])
        plt.stackplot(x, alive, starved, zapped, colors=['#4FADAC', '#5386A6', '#2F5373'], labels=[r"Alive", r"Starved", r"Zapped"])

    for i, ax in enumerate(axes):
        ax.set(ylim=(0,100))
        ax.set(xlim=(0, 50))
        ax.set_ylabel(r"Gopher Status (%)", fontsize=10)
        ax.set_xlabel(r"Time (# of Traps Seen)", fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=10, direction='in')
        ax.set_aspect(1.0/ax.get_data_ratio(), adjustable='box')
        ax.legend()
        ax.set_title(r"Status Over Time" + "\n" + modes[i] + "\n" + "(" + fitnessFunc + ")", fontsize=11)

    for i, fig in enumerate(figs):
        fig.tight_layout()
        filename = constants.getExperimentResultPath(number=2, func=fitnessFunc, suff='_stackplot'+str(i+1), fileType="pdf")
        fig.savefig(filename, bbox_inches='tight', pad_inches=0)
    
    plt.close('all')




def filterDataFrame(data, filterlist):
    """filters a data frame according to a filterlist
    filterlist: [[param1, value], [param2, value] ...]"""
    data = copy.deepcopy(data)
    for param, value in filterlist:
        booleans = data[param] == value
        data = data[booleans]
    return data