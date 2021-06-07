import csv
import copy
import pandas as pd
import matplotlib.pyplot as plt
import statistics as stats
import math as m

paramLabels = {
        "defaultProbEnter":r"Default Probability of Entering Trap",
        "probReal":r"Probability of Encountering a Designed Trap",
        "nTrapsWithoutFood":r"Maximum Fasting Interval",
        "maxProjectileStrength":r"Maximum Projectile Strength",
    }

def allDataToCSV(allData, filename):
    """takes in a data list obtained from simulateManySetups and writes all of the run information into a csv"""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["BATCH #"] + ["RUN #"] + [key for key in allData[0]["runsData"][0]]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for batchIndex in range(len(allData)):
            batchData = allData[batchIndex]
            runsData = batchData["runsData"]
            for runIndex in range(len(runsData)):
                runDict = runsData[runIndex]
                runDict["BATCH #"] = batchIndex
                runDict["RUN #"] = runIndex
                writer.writerow(runDict)

def listStats(numList):
    """takes in a list of numbers and returns [average, standard deviation, 95% confidence interval]"""
    avg = stats.mean(numList)
    std = stats.stdev(numList)
    sem = std / m.sqrt(len(numList))
    z = 1.96 # 95% ci
    ci = (avg - z*sem, avg + z*sem)
    return [avg, std, ci]

def proportionStats(portion, total):
    """returns the percentage and confidence interval of the portion"""
    p = portion / total
    ci = 196 * m.sqrt((p * (1-p))/total)
    p *= 100
    return p, (p-ci, p+ci)

def filterDataFrame(data, filterlist):
    """filters a data frame according to a filterlist
    filterlist: [[param1, value], [param2, value] ...]"""
    data = copy.deepcopy(data)
    for param, value in filterlist:
        booleans = data[param] == value
        data = data[booleans]
    return data

def percentThoughtReal(filename, param):
    """given the filename of a run including intention gophers, 
    prints out the frequency that intention gophers thought traps 
    were real (varying with the indicated parameter)"""
    data = pd.read_csv(filename)
    data = filterDataFrame(data, [["intention", True]])
    for val, group in data.groupby(param):
        print(val)
        groupThoughtReal = 0
        groupTrapsPresentedWith = 0
        for index, gopher in group.iterrows():
            groupThoughtReal += gopher["numThoughtReal"]
            groupTrapsPresentedWith += gopher["numTraps"] + (gopher["status"] == 2) #if zapped, it saw one more trap than it survived
        print(groupThoughtReal / groupTrapsPresentedWith)
        print()


def linearRunGraph(filename, param):
    """Saves a graph displaying information about the given parameter from the data in the given file"""

    labelsize = 18
    legendsize = 16
    titlesize = 19
    ticksize = 16
    linewidth = 3

    data = pd.read_csv(filename)
    plt.style.use('ggplot')
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
        
    df0 = filterDataFrame(data, [["intention", True], ["cautious", False]])
    df1 = filterDataFrame(data, [["intention", False]])
    df3 = filterDataFrame(data, [["intention", True], ["cautious", True]])

    dfs = [df0, df1, df3]
    modes = [r"With Intention", r"Without Intention", r"Cautious"]

    colorIter = iter(['#4FADAC', '#2F5373', '#C59CE6'])
    
    fig, axes = plt.subplots(1,3, figsize=(18,6.5))
    life_ax, food_ax, n_food_ax = axes.flat

    for i in range(2): # change to 3 if including cautious (for pr graph)
        df = dfs[i]
        paramValues = []

        trap_vals = []
        t_up_ci = []
        t_low_ci = []

        food_vals = []
        f_up_ci = []
        f_low_ci = []

        n_food_vals = []
        n_f_up_ci = []
        n_f_low_ci = []

        for val, group in df.groupby(param):
            paramValues.append(val)

            group_vals = group["numTraps"]
            groupLifeTimes = []
            for numTraps in group_vals:
                numTraps = int(numTraps)
                groupLifeTimes.append(numTraps)
            avg, std, ci = listStats(groupLifeTimes)
            trap_vals.append(avg)
            t_low_ci.append(ci[0])
            t_up_ci.append(ci[1])

            group_vals = group["numFood"]
            groupNumFood = []
            for numFood in group_vals:
                numFood = int(numFood)
                groupNumFood.append(numFood)
            avg, std, ci = listStats(groupNumFood)
            food_vals.append(avg)
            f_low_ci.append(ci[0])
            f_up_ci.append(ci[1])
            
            groupFoodPerTrap = [groupNumFood[j] / groupLifeTimes[j] for j in range(len(groupNumFood)) if groupLifeTimes[j] != 0] #we discard when insufficient data
            avg, std, ci = listStats(groupFoodPerTrap)
            n_food_vals.append(avg)
            n_f_low_ci.append(ci[0])
            n_f_up_ci.append(ci[1])
           
        color = next(colorIter)
        life_ax.plot(paramValues, trap_vals, label=modes[i], color=color, linewidth=linewidth)
        life_ax.fill_between(paramValues, t_low_ci, t_up_ci, color=color, alpha=.15)

        food_ax.plot(paramValues, food_vals, label=modes[i], color=color, linewidth=linewidth)
        food_ax.fill_between(paramValues, f_low_ci, f_up_ci, color=color, alpha=.15)

        n_food_ax.plot(paramValues, n_food_vals, label=modes[i], color=color, linewidth=linewidth)
        n_food_ax.fill_between(paramValues, n_f_low_ci, n_f_up_ci, color=color, alpha=.15) 
    
    life_ax.set(ylim=(0, 50))
    life_ax.set_ylabel(r"Gopher Lifespan (number of traps)", fontsize=labelsize, fontweight='bold')
    life_ax.set_xlabel(paramLabels[param], fontsize=labelsize, fontweight='bold')
    life_ax.tick_params(axis='both', which='major', labelsize=ticksize, direction='in')
    life_ax.set_title(r"Gopher Lifespan" + "\n" + r"vs" + "\n" + paramLabels[param], fontsize=titlesize, fontweight='bold')
    life_ax.legend(prop={"size":legendsize})

    food_ax.set(ylim=(0, 50))
    food_ax.set_ylabel(r"Amount of Food Consumed", fontsize=labelsize, fontweight='bold')
    food_ax.set_xlabel(paramLabels[param], fontsize=labelsize, fontweight='bold')
    food_ax.tick_params(axis='both', which='major', labelsize=ticksize, direction='in')
    food_ax.set_title(r"Food Consumption" + "\n" + r"vs" + "\n" + paramLabels[param], fontsize=titlesize, fontweight='bold')
    food_ax.legend(prop={"size":legendsize})

    n_food_ax.set(ylim=(0, 1))
    n_food_ax.set_ylabel(r"Food Consumed Per Trap Survived", fontsize=labelsize, fontweight='bold')
    n_food_ax.set_xlabel(paramLabels[param], fontsize=labelsize, fontweight='bold')
    n_food_ax.tick_params(axis='both', which='major', labelsize=ticksize, direction='in')
    n_food_ax.set_title(r"Normalized Food Consumption" + "\n" + r"vs" + "\n" + paramLabels[param], fontsize=titlesize, fontweight='bold')
    n_food_ax.legend(prop={"size":legendsize})

    fig.tight_layout()
    fig.savefig(param + '.pdf', bbox_inches='tight', pad_inches=0)
    plt.close('all')






def statusOverTime(filename):
    """displays a graph with information about the lifes of intention and normal gophers"""

    data = pd.read_csv(filename)
    plt.style.use('ggplot')
    # plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
        
    df0 = filterDataFrame(data, [["intention", True]])
    df1 = filterDataFrame(data, [["intention", False]])

    dfs = [df0, df1]
    modes = [r"With Intention Perception", r"Without Intention Perception"]

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
        ax.set_title(r"Status Over Time" + "\n" + modes[i], fontsize=11)

    for i, fig in enumerate(figs):
        fig.tight_layout()
        fig.savefig('stackplot{}.pdf'.format(i+1), bbox_inches='tight', pad_inches=0)
    
    plt.close('all')

