import libs.simulation as s
import copy
import csv
import geneticAlgorithm.utils as utils
import geneticAlgorithm.fitnessFunctions as ff
from classes.Encoding import Encoding
import classes.Trap as t
import numpy as np
import matplotlib.pyplot as plt
import legacy.magicFunctions as mf
import legacy.data as d
import geneticAlgorithm.constants as constants
import geneticAlgorithm.analytical as analy
import geneticAlgorithm.library as lib


pref = {
    "intention" : 1, #if gopher has intention
    "defaultProbEnter" : 0.8, #probability of gopher entering trap (not for intention)
    "probReal" : 0.0, #percentage of traps that are designed as opposed to random, set default to 0
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
        "probReal" : 0.0,
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
        # if functional:
        #     trap = t.Trap(rowLength, colLength, functional)
        # else:
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



def analyticalStatusofGopher(fitnessFunc):
    """
    Takes in a fitness funcion, return a list of 50 tuples (P_alive, P_starved, P_zapped) 
    representing the status of gophers at the ith trap
    """
    """
    Idea:
        1. the gopher enter the trap
            a. the gopher eat the food
                -the gopher is zapped -> Z
                -the gopher is not zapped -> H0
            b. the gopher doesn't eat the food
                -the gopher is zapped -> Z
                -the gopher is not zapped -> H_n+1 or S(when n=3)
        2. the gopher didn't enter the trap -> H_n+1 or S(when n=3)
    """
    numFiles = 25
    MFI = 4
    trapList = loadTrapList(fitnessFunc, numFiles)
    encoder = Encoding(code = 1)
    ## Calcualted average probability of killing a gopher/firing/
    killSum = 0
    fireSum = 0
    eatSum = 0
    eatAndDeathSum = 0
    notEatAndDeathSum = 0
    for trap in trapList:
        # whether it kills
        encodedTrap = encoder.encode(trap.board)
        lethality = ff.getLethality(encodedTrap, encoder)
        probKill = lethality * constants.MAX_PROB_DEATH
        killSum += probKill
        # whether it fires
        fireSum += analy.shootProjectile(trap.board)
        # whether gopher eats
        eatTimeDist = analy.getProbabilityDistribution(constants.DEFAULT_PROB_ENTER)
        expectedEatTime = sum([eatTimeDist[i] * (i+1) for i in range(len(eatTimeDist))])
        eatSum += analy.doesGopherEat(trap.board, expectedEatTime)
        # whether gopher eats and dies
        timeDist = analy.getProbabilityDistribution(constants.DEFAULT_PROB_ENTER)
        sumProb1 = 0
        for i, dist in enumerate(timeDist):
            eatAndDeathProb = analy.probGopherEatAndDie(trap.board, i+1)
            sumProb1 += (eatAndDeathProb * dist)
        eatAndDeathSum += sumProb1
        # whether gopher doesn't eat and dies
        timeDist = analy.getProbabilityDistribution(constants.DEFAULT_PROB_ENTER)
        sumProb2 = 0
        for i, dist in enumerate(timeDist):
            eatAndDeathProb = analy.probNotEatAndDie(trap.board, i+1)
            sumProb2 += (eatAndDeathProb * dist)
        notEatAndDeathSum += sumProb2

    expectedProbKill = killSum / len(trapList)
    expectedProbFire = fireSum / len(trapList)
    expectedProbEat = eatSum / len(trapList)
    expectedProbEatAndDeath = eatAndDeathSum / len(trapList)
    expectedProbNotEatAndDeath = notEatAndDeathSum / len(trapList)

    print("expectedProbKill", expectedProbKill)
    print("expectedProbFire", expectedProbFire)
    print("expectedProbEat", expectedProbEat)
    print("expectedProbEatAndDeath", expectedProbEatAndDeath)
    print("expectedProbNotEatAndDeath", expectedProbNotEatAndDeath)
    # 
    hungerStatus = [1, 0, 0, 0]
    probZapped = [0] * 51
    probStarved = [0] * 51
    probAlived = [1] * 51

    for i in range(1, 51):
        if probAlived[i-1] == 0:
            probAlived[i] = probAlived[i-1]
            probStarved[i] = probStarved[i-1]
            probZapped[i] = probZapped[i-1]
        else:
            normalizedHungerStatus = np.array(hungerStatus) / sum(hungerStatus)
            expectedHungerLevel = sum([normalizedHungerStatus[i] * i for i in range(4)])
            hungerWeight = ((expectedHungerLevel + 1) / MFI)**10
            probEnter = 1 if hungerWeight == 1 else constants.DEFAULT_PROB_ENTER * (1 - hungerWeight) + hungerWeight
            # probEnter = 1
            #################
            # probGopherEat = probEnter * ( expectedProbFire * expectedProbEat + (1 - expectedProbFire) * 1 - expectedProbKill) 
            probEatAndAlive = probEnter * (expectedProbEat - expectedProbEatAndDeath)
            probEatAndDeath = probEnter * (expectedProbEatAndDeath)
            probNotEatAndAlive = probEnter * ((1-expectedProbEat) - expectedProbNotEatAndDeath) + (1-probEnter)
            probNotEatAndDeath = probEnter * expectedProbNotEatAndDeath
            
            probStarved[i] = probStarved[i-1] + hungerStatus[3] * probNotEatAndAlive
            probZapped[i] = probZapped[i-1] + probAlived[i-1] * (probEatAndDeath + probNotEatAndDeath)
            probAlived[i] = 1 - probStarved[i] - probZapped[i]
            hungerStatus[3] = hungerStatus[2] * probNotEatAndAlive
            hungerStatus[2] = hungerStatus[1] * probNotEatAndAlive
            hungerStatus[1] = hungerStatus[0] * probNotEatAndAlive
            hungerStatus[0] = probAlived[i-1] * probEatAndAlive


        print("alived:", probAlived[i])
        print("sum of status:", sum(hungerStatus))
        print(hungerStatus)

    
    x = [t for t in range(51)]
    plt.stackplot(x, probAlived, probStarved, probZapped, colors=['#4FADAC', '#5386A6', '#2F5373'], labels=[r"Alive", r"Starved", r"Zapped"])
    plt.xlabel('Time (# of Traps Seen)')
    plt.ylabel('Gopher Status (%)')
    plt.legend()
    plt.title('Status Over Time \
    Without Intention')
    plt.show()
    plt.savefig('test.png')
