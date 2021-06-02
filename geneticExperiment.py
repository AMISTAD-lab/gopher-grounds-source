from geneticAlgorithm.fitnessFunctions import coherentFitness
import simulation as sim
from geneticAlgorithm.encoding import singleDecoding
import geneticAlgorithm.utils as utils
import numpy as np
from scipy.stats import norm
import os

def runSimulations(encodedTrap, numSimulations=10000, conf_level=0.95, intention=False, printStatistics = True):
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
    proportion = numberAlive / (numSimulations * hungerLevels)
    stderr = np.sqrt(proportion * (1 - proportion) / (numSimulations * hungerLevels))
    z_score = norm.ppf(conf_level)
    conf_interval = (
        round(proportion + z_score * stderr, 3), \
        round(proportion - z_score * stderr, 3)
    )

    if printStatistics:
        print('Proportion: ', proportion)
        print('Std Error: ', round(stderr, 3))
        print('CI: [', round(conf_interval[0], 3), ', ', round(conf_interval[1], 3), ']')

    return proportion, stderr, conf_interval

def runExperiment(fitnessFunc, threshold, measure='max', maxIterations=1000, showLogs=True, 
    improvedCallback=True, numSimulations=10000, conf_level=0.95, intention=False, printStatistics=True, export=False, outputFile='experiment.txt'):
    '''
    Creates a trap using the genetic algorithm (optimized for the input fitness function) and
    conducts an experiment using that trap. The experiment calculates the probability that the gopher
    survives the trap, along with a confidence interval. Can optionally export the findings to another file.
    Returns a 5-tuple of (trap, fitness, proportion, stderr, conf_interval)
    '''
    # File to export the genetic output data
    geneticAlgFile = 'geneticAlgorithm.txt'
    trap = []
    fitness = 0
    if export:
        trap, fitness = utils.exportGeneticOutput(geneticAlgFile, utils.cellAlphabet, fitnessFunc, threshold, measure, maxIterations, showLogs, improvedCallback)
    else:
        trap, fitness = utils.geneticAlgorithm(utils.cellAlphabet, fitnessFunc, threshold, measure, maxIterations, showLogs, improvedCallback)

    proportion, stderr, conf_interval = runSimulations(trap, numSimulations, conf_level, intention, printStatistics)

    if export:
        firstLine = 'Total Experiments: '
        # Check if the file exists first
        if not os.path.isfile('./' + outputFile):
            with open(outputFile, 'w+') as out:
                out.write(firstLine + '0\n')
                out.close()

        # Write the data from the experiment to the file
        experimentNum = 0
        fileLines = []
        with open(outputFile, 'r') as out:
            fileLines = out.readlines()
            
            # Handling malformed files
            if fileLines == []:
                fileLines = [firstLine + '0\n']
            
            experimentNum = int(fileLines[0][len(firstLine):].strip()) + 1
            fileLines[0] = firstLine + str(experimentNum) + '\n'
            out.close()

        with open(outputFile, 'w') as out:
            out.writelines(fileLines)
            out.close()

        with open(outputFile, 'a') as out:
            out.write('\n')
            out.write('Experiment {}\n'.format(experimentNum))
            out.write('-------------\n')
            out.write('Best Trap\t\t\t:\t')
            
            # Print array
            out.write('[ ')
            
            # Convert to array form
            for j, digit in enumerate(trap):
                out.write(str(digit))
                
                if j < len(trap) - 1:
                    out.write(', ')
            
            out.write(' ]\n')
            out.write('Fitness\t\t\t\t:\t{}\n'.format(str(fitness)))
            out.write('Proportion\t\t\t:\t{}\n'.format(round(proportion, 4)))
            out.write('Standard Error\t\t:\t{}\n'.format(round(stderr, 3)))
            out.write('Confidence Interval\t:\t({}, {})\n'.format(round(conf_interval[0], 3), round(conf_interval[1], 3)))
            out.write('\n')
            out.close()
    
    return trap, fitness, proportion, stderr, conf_interval