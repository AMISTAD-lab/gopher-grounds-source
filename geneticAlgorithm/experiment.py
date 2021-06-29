import csv
import numpy as np
import os
from progress.bar import IncrementalBar
from scipy.stats import norm
import geneticAlgorithm.constants as constants
from geneticAlgorithm.encoding import singleDecoding
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.utils as utils
from geneticAlgorithm.main import geneticAlgorithm
import libs.simulation as sim
import misc.csvUtils as csvUtils

def runSimulations(encodedTrap, numSimulations=10000, confLevel=0.95, intention=False, printStatistics = True):
    '''
    Takes in an encoded trap and runs `numSimulations` simulations at 5 different hunger levels.
    Tallies the number of alive gophers and returns the proportion of alive gophers as well as the
    standard error.
    '''
    decodedTrap = singleDecoding(encodedTrap)

    numberAlive = 0
    hungerLevels = 5
    for _ in range(int(numSimulations)):
        for hunger in range(hungerLevels):
            numberAlive += int(sim.simulateTrap(utils.createTrap(decodedTrap), intention, hunger = hunger / 5)[3])

    # Calculate statistics
    proportion = 1 - numberAlive / (numSimulations * hungerLevels)
    stderr = np.sqrt(proportion * (1 - proportion) / (numSimulations * hungerLevels))
    z_score = norm.ppf(confLevel + (1 - confLevel) / 2)
    conf_interval = (
        round(proportion - z_score * stderr, 3), \
        round(proportion + z_score * stderr, 3)
    )

    if printStatistics:
        print('Proportion: ', proportion)
        print('Std Error: ', round(stderr, 3))
        print('CI: [', round(conf_interval[0], 3), ', ', round(conf_interval[1], 3), ']')

    return proportion, stderr

def runExperiment(fitnessFunc, threshold, maxGenerations=10000, showLogs=True, numSimulations=5000, printStatistics=True, trialNo=0, barData={}, writer=None):
    '''
    Creates a trap using the genetic algorithm (optimized for the input fitness function) and
    conducts an experiment using that trap. The experiment calculates the probability that the gopher
    survives the trap, along with a confidence interval. Can optionally export the findings to another file.
    Returns a list of 2 5-tuples of (trap (encoded), fitness, proportion, stderr, intention), where intention
    is varied between True and False
    '''
    # Defining the function name for logging purposes
    functionName = ''
    if fitnessFunc == functions.randomFitness:
        functionName = 'random'
    elif fitnessFunc == functions.coherentFitness:
        functionName = 'coherence'
    elif fitnessFunc == functions.functionalFitness:
        functionName = 'functional'
    elif fitnessFunc == functions.multiobjectiveFitness:
        functionName = 'multiobjective'

    # Generate the trap (either by exporting to a file or calling the genetic algorithm)
    _, trap, fitness = geneticAlgorithm(constants.CELL_ALPHABET, fitnessFunc, threshold, maxGenerations, showLogs, trial=trialNo, functionName=functionName, barData=barData, writer=writer)

    # Run the experiment on the generated (optimized) trap
    retList = []
    for intention in (True, False):
        proportion, stderr = runSimulations(trap, numSimulations=numSimulations, intention=intention, printStatistics=printStatistics)
        retList.append([trap, fitness, proportion, stderr, intention])
    
    return retList

def runBatchExperiments(numExperiments, fitnessFunction, threshold, numSimulations = 5000, maxGenerations=10000, showLogs=False, overwrite=False, suffix=''):
    """Runs an experiment `numExperiments` times with the given parameters and exports it to a .csv file"""
    # Defining the function name for logging purposes
    functionName = ''
    fof = {}
    if fitnessFunction == functions.randomFitness:
        functionName = 'random'
    elif fitnessFunction == functions.coherentFitness:
        functionName = 'coherence'
    elif fitnessFunction == functions.functionalFitness:
        functionName = 'functional'
    elif fitnessFunction == functions.multiobjectiveFitness:
        functionName = 'multiobjective'

    experimentNum = 0

    frequencyPath = constants.frequencyPath.format(functionName, suffix)
    experimentPath = constants.experimentPath.format(functionName, suffix)

    # If the path exists but not the file, or we are overwriting the file, create it
    csvUtils.updateCSV(frequencyPath, headers=constants.frequencyHeaders, overwrite=overwrite)
    csvUtils.updateCSV(experimentPath, headers=constants.experimentHeaders, overwrite=overwrite)

    numBars = 1000
    maxSteps = numExperiments * maxGenerations
    
    # Run the experiment many times
    with IncrementalBar('Fraction done: ', max = numBars) as bar:
        with open(frequencyPath, 'a', newline='') as freqOut:
            freqWriter = csv.writer(freqOut)

            for i in range(numExperiments):
                # Clearing old write data
                writeData = []

                # Generates and runs simulations on a trap, returning experiment data
                experimentData = runExperiment(
                    fitnessFunction,
                    threshold,
                    maxGenerations,
                    showLogs=showLogs,
                    numSimulations=numSimulations,
                    printStatistics=False,
                    trialNo=i+1,
                    barData={ 'counter': 0, 'bar': bar, 'maxSteps': maxSteps, 'numBars': numBars },
                    writer=freqWriter
                )

                # Writes the experiment data to a CSV (len(experimentData) == 2)
                for j, [trap, fitness, proportion, stderr, intention] in enumerate(experimentData):
                    trapStr = utils.convertEncodingToString(trap)

                    writeData.append([
                        (experimentNum + i) * 2 + j,
                        trapStr,
                        functionName,
                        round(fitness, 4),
                        int(intention),
                        round(functions.functionalFitness(trap), 4),
                        round(functions.coherentFitness(trap), 4),
                        round(functions.combinedFitness(trap), 4),
                        round(proportion, 4), round(stderr, 4)
                    ])

                # Write data to csv
                csvUtils.updateCSV(experimentPath, writeData)

                # Commit changes to files and flush buffers
                freqOut.flush()
                os.fsync(freqOut)

            bar.finish()
        
    print("SIMULATION FINISHED.\n")

def createFoF(func, suffix=''):
    '''
    Take in a fitness function (and optional suffix) and create a frequency of
    frequency dictionary from the frequency file generated
    '''
    fof = {}
    freqs = {}

    freqPath = constants.frequencyPath.format(func, suffix)

    with open(freqPath, 'r', newline='') as fRead:
        reader = csv.reader(fRead)

        for i, [_, _, trap, *_] in enumerate(reader):
            if i == 0:
                continue

            functions.updateFreqs(trap, freqs, fof)

            if freqs[trap] == 4:
                bestTrap = trap

    fofPath = constants.fofPath.format(func, suffix)
    fofData = [[key, fof[key]] for key in sorted(fof.keys())]

    csvUtils.updateCSV(fofPath, fofData, constants.fofHeaders, True)
    