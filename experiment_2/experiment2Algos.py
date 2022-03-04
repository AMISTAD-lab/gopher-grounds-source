import libs.simulation as s
import copy
import csv
import geneticAlgorithm.utils as utils
from classes.Encoding import Encoding
import classes.Trap as t
import numpy as np
import legacy.magicFunctions as mf
import legacy.data as d
import geneticAlgorithm.constants as constants
import geneticAlgorithm.analytical as analy
import geneticAlgorithm.library as lib


pref = {
    "intention" : 1, #if gopher has intention
    "defaultProbEnter" : 0.8, #probability of gopher entering trap (not for intention)
    "probReal" : 0.2, #percentage of traps that are designed as opposed to random, set default to 0
    "nTrapsWithoutFood" : 4, #the amount of traps a gopher can survive without entering (due to starvation)
    "maxProjectileStrength" : 0.45, #thickWire strength
}

def runExperiment(filename, inputToVary, numSimulations, numFiles, fitnessFunc):
    """runs the experiment on the indicated parameter input and saves the data to a csv"""
    trapList = loadTrapList(fitnessFunc, numFiles)
    inputfile = createExpInputFile(inputToVary)
    seedList = createSeedListFromFile(inputfile)
    allData = simulateManySetups(numSimulations, seedList, fitnessFunc, trapList)
    d.allDataToCSV(allData, filename)

def createExpInputFile(inputToVary):
    """Inputs:
        inputToVary: String, the input to vary. 
            eg. "predSightDistance"
        startValue: the starting value of input, inclusive
        endingValue: the ending value of input, inclusive
        stepValue: the stepValue for input
    """
    filename = "experimentInput.txt"
    file = open(filename, "w")
    for intention in [0, 1]:
        toWrite = "intention " + str(intention) + "\n" 
        if inputToVary == "probReal":
            for percent in range(0, 100+1, 5):
                percent /= 100
                file.write(toWrite)
                file.write("probReal " + str(percent) + "\n\n")
        elif inputToVary == "nTrapsWithoutFood":
            for n in range(1, 5+1, 1):
                file.write(toWrite)
                file.write("nTrapsWithoutFood " + str(n) + "\n\n")
        elif inputToVary == "maxProjectileStrength":
            for probKill in range(3, 99+1, 6):
                probKill /= 100
                file.write(toWrite)
                file.write("maxProjectileStrength " + str(probKill) + "\n\n")
        elif inputToVary == "defaultProbEnter":
            for probEnter in range(0, 100+1, 5):
                probEnter /= 100
                file.write(toWrite)
                file.write("defaultProbEnter " + str(probEnter) + "\n\n")
        elif inputToVary == "default":
            file.write(toWrite + "\n")
        else:
            raise Exception("Something went wrong")
    file.close() 
    return filename


def createSeedListFromFile(filename):
    seedFile = open(filename, "r")
    lineList = seedFile.readlines()
    seedFile.close()
    lineList = [x.strip("\n") for x in lineList]
    lineList = lineList[:-1]

    standardSeed = {
        "intention" : 1,
        "defaultProbEnter" : 0.8,
        "probReal" : 0.2,
        "nTrapsWithoutFood" : 4,
        "maxProjectileStrength" : 0.45,
    }

    seedList = []
    preferences = copy.deepcopy(standardSeed)
    for line in lineList:
        if line == "":
            seedList.append(preferences)
            preferences = copy.deepcopy(standardSeed)
        else:
            key, value = line.split()
            if key in preferences:
                preferences[key] = float(value)
    seedList.append(preferences)
    return seedList


def simulateManySetups(numSimulations, seedList, fitnessFunc, trapList):
    allData = []
    numSeeds = len(seedList)
    for i in range(numSeeds):
        allData.append(batchSimulate(numSimulations, seedList[i], fitnessFunc, trapList, [True, i, numSeeds]))
    return allData


def batchSimulate(numSimulations, pref, fitnessFunc, trapList, manySetups=[False,0,0]):
    """runs simulate many times"""
    batchData = copy.deepcopy(pref) # holds runData, as well as averages for each set of parameters
    runsData = [] # holds data dictionaries for runs with a given set of parameters. (greater number of runs = greater precision)
    for i in range(numSimulations):
        data, trapInfo = simulate(pref, fitnessFunc, trapList)
        runsData.append(data)
        if manySetups[0]:
            printProgressBar((i+1) + (manySetups[1] * numSimulations), numSimulations * manySetups[2])
    batchData["runsData"] = runsData 
    return batchData

def simulate(pref, fitnessFunc, trapList):
    intention = pref["intention"]
    probReal = pref["probReal"]
    nTrapsWithoutFood = pref["nTrapsWithoutFood"]

    mf.initializeVariablesNew(pref, fitnessFunc)

    stillAlive = True
    trapsWithoutFood = 0
    numTraps = 0
    killedByHunger = False
    trapInfo = []
    numFood = 0
    numThoughtReal = 0
    while stillAlive and numTraps < 50:
        rowLength = 3
        colLength = 4
        functional = np.random.binomial(1, probReal)
        if functional:
            trap = t.Trap(rowLength, colLength, functional)
        else:
            trap = np.random.choice(trapList)
        hunger = (trapsWithoutFood + 1)/nTrapsWithoutFood
        ib, ac, gc, alive, eaten, thoughtReal = s.simulateTrap(trap, intention, hunger)
        numThoughtReal += thoughtReal
        trapInfo.append([ib, ac, gc])
        stillAlive = alive
        if alive:
            numTraps += 1
            if eaten:
                numFood += 1
                trapsWithoutFood = 0
            else:
                trapsWithoutFood += 1
            if trapsWithoutFood >= nTrapsWithoutFood:
                killedByHunger = True
                stillAlive = False
    
    data = copy.deepcopy(pref)
    data["numTraps"] = numTraps
    if stillAlive:
        data["status"] = 0 #alive
    elif killedByHunger:
        data["status"] = 1 #starved
    else:
        data["status"] = 2 #zapped
    data["numFood"] = numFood
    data["numThoughtReal"] = numThoughtReal
    return data, trapInfo

def expectedLethality(n, r):
    """randomly samples n boards, runs each r times, and then returns the expected lethality calculated from the gopher entering"""
    lethal = 0.0
    traps = [t.Trap(3,4,False,trapboard) for trapboard in t.sampleRandomBoards(n)]
    total = len(traps)
    runs = total*r
    trapInfo = []
    for i in range(total):
        for j in range(r):
            printProgressBar(i*r + j + 1, runs)
            ib, ac, gc, alive, eaten = s.simulateTrap(traps[i], True)
            if alive == False:
                lethal += 1
    print("\nlethal runs:", lethal, "\ntotal runs:", runs, "\nnum traps:", total)
    runs = float(runs)
    p = lethal / runs
    ci = 1.96*(p*(1-p))/runs
    p *= 100
    ci *= 100
    print("%s +/- %s" % (p, ci))
    return trapInfo

def printProgressBar (iteration, total, prefix = 'Progress:', suffix = 'Complete', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


def loadTrapList(fitnessFunc, numFiles, encoder: Encoding = None):
    if not encoder:
        encoder = Encoding(code = 1)
    countTotal = 0
    trapList = []
    for i in range(numFiles):
        input_suff = "_new_enc_{}".format(i + 1)
        inputPath = constants.getExperimentPath(func=fitnessFunc, suff=input_suff)
        with open(inputPath, 'r' ,newline='') as incsv:
            for row in csv.reader(incsv):
                if row[0] == "Experiment":
                    continue
                else:
                    countTotal += 1
                    if countTotal % 2 == 0:
                        continue
                    encodedTrap = utils.convertStringToEncoding(row[2])
                    decodedTrap = encoder.decode(encodedTrap)
                    trap = utils.createTrap(decodedTrap)
                    trapList.append(trap)
    return trapList


