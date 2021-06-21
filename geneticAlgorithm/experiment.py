import csv
import numpy as np
import os
import pandas as pd
from scipy.stats import norm
import geneticAlgorithm.constants as constants
from geneticAlgorithm.encoding import singleDecoding
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.utils as utils
import libs.simulation as sim

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

    return proportion, stderr, conf_interval

def runExperiment(fitnessFunc, threshold, measure='max', maxIterations=10000, showLogs=True, 
    improvedCallback=True, callbackFactor=0.95, numSimulations=10000, confLevel=0.95, intention=False, printStatistics=True, export=False, outputFile='experiment.txt'):
    '''
    Creates a trap using the genetic algorithm (optimized for the input fitness function) and
    conducts an experiment using that trap. The experiment calculates the probability that the gopher
    survives the trap, along with a confidence interval. Can optionally export the findings to another file.
    Returns a 5-tuple of (trap (encoded), fitness, proportion, stderr, conf_interval)
    '''
    # File to export the genetic output data
    trap = []
    fitness = 0

    # Generate the trap (either by exporting to a file or calling the genetic algorithm)
    _, trap, fitness = utils.geneticAlgorithm(constants.CELL_ALPHABET, fitnessFunc, threshold, measure, maxIterations, showLogs, improvedCallback, callbackFactor)

    # Run the experiment on the generated (optimized) trap
    proportion, stderr, conf_interval = runSimulations(trap, numSimulations, confLevel, intention, printStatistics)

    # Write to the file if we are exporting
    if export:
        firstLine = 'Total Experiments: '
        
        # Defining the function name for logging purposes
        functionName = ''
        if fitnessFunc == functions.randomFitness:
            functionName = 'random'
        elif fitnessFunc == functions.coherentFitness:
            functionName = 'coherence'
        elif fitnessFunc == functions.functionalFitness:
            functionName = 'functional'
        elif fitnessFunc == functions.combinedFitness:
            functionName = 'combined'

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
            out.write('Trap\t\t\t\t:\t')
            
            # Print array
            out.write('[ ')
            
            # Convert to array form
            for j, digit in enumerate(trap):
                out.write(str(digit))
                
                if j < len(trap) - 1:
                    out.write(', ')
            
            out.write(' ]\n')

            # Write statistics
            out.write('Fitness\t\t\t\t:\t{}\n'.format(str(round(fitness, 3))))
            out.write('Function\t\t\t:\t{}\n'.format(functionName))
            out.write('Proportion Dead\t\t:\t{}\n'.format(round(proportion, 4)))
            out.write('Standard Error\t\t:\t{}\n'.format(round(stderr, 3)))
            out.write('Confidence Interval\t:\t[{}, {}]\n'.format(round(conf_interval[0], 3), round(conf_interval[1], 3)))
            out.write('Intention?\t\t\t:\t{}\n'.format('Yes' if intention else 'No'))
            out.write('\n')
            out.close()
    
    return trap, fitness, proportion, stderr, conf_interval, intention

def runBatchExperiments(numExperiments, fitnessFunction, threshold, numSimulations = 10000, maxIterations=10000, confLevel=0.95, showLogs=False, outputFile='experiment.csv', intention=False, improvedCallback=True, callbackFactor=0.95, overwrite=False):
    """Runs an experiment `numExperiments` times with the given parameters and exports it to a .csv file"""
    headers = ['Experiment', 'Trap', 'Fitness', 'Fitness_Funct', 'Prop_Dead', 'Stand_Err','Conf_Interval', 'Intention?', 'Threshold']

    if outputFile[-4:] != '.csv':
        raise Exception('Please enter a valid file extension for the output file. {} was given'.format(outputFile))

    # Defining the function name for logging purposes
    functionName = ''
    if fitnessFunction == functions.randomFitness:
        functionName = 'random'
    elif fitnessFunction == functions.coherentFitness:
        functionName = 'coherence'
    elif fitnessFunction == functions.functionalFitness:
        functionName = 'functional'
    elif fitnessFunction == functions.combinedFitness:
        functionName = 'combined'

    experimentNum = 0
    directory = './csv/{}/'.format(functionName)
    filePath = '{}{}'.format(directory, outputFile)

    if not os.path.exists(directory):
        os.mkdir(directory)
    elif not os.path.isfile(filePath) or overwrite:
        with open(filePath, 'w+') as out:
            writer = csv.writer(out)
            writer.writerow(headers)
            out.close()
    else:
        isPopulated = False
        with open(filePath, 'r') as out:
            reader = csv.reader(out)
            for line in reader:
                isPopulated = True
                if line[0] == headers[0]:
                    continue
                experimentNum = int(line[0])
            out.close()

        if not isPopulated:
            with open(filePath, 'w') as out:
                writer = csv.writer(out)
                writer.writerow(headers)
            out.close()

    # Run the experiment many times
    for i in range(numExperiments):
        print('STARTING EXPERIMENT {}.\n'.format(i + 1))

        # Clearing old write data
        writeData = []

        trap, fitness, proportion, stderr, conf_interval, intention = runExperiment(
            fitnessFunction,
            threshold,
            'max',
            maxIterations,
            showLogs,
            improvedCallback,
            callbackFactor,
            numSimulations,
            confLevel,
            intention,
            False,
            export=False
        )

        trapStr = utils.convertEncodingToString(trap)

        writeData = [experimentNum + i + 1, trapStr, round(fitness, 4), functionName, round(proportion, 4), round(stderr, 4), conf_interval, intention, threshold]
        print('FINISHED EXPERIMENT {}.\n\n'.format(i + 1))

        # Write data to csv
        with open(filePath, 'a') as out:
            writer = csv.writer(out)
            writer.writerow(writeData)
            out.close()
        
        
    print("SIMULATION FINISHED.")

def updateFrequencyCSV(fileName, fitnessFunc, freqDict):
    """
    Updates the frequencies in CSVs when a new batch run experiments is issued
    """
    if fileName[-4:] == '.csv':
        fileName = fileName[:-4]

    directory = './frequencies/{}'.format(fitnessFunc)
    filePath = '{}/{}Freqs.csv'.format(directory, fileName)
    headers = ['Trap', 'Freq']

    # If the path does not exist, then create it
    if not os.path.isfile('./' + filePath):
        if not os.path.exists(directory):
            os.mkdir(directory)

        with open(filePath, 'w') as out:
            writer = csv.writer(out)
            writer.writerow(headers)
            out.close()

    # Read in the CSV as a dataframe to allow for easy manipulation
    df = pd.read_csv('./' + filePath, index_col=0)

    # Update all of the known keys with the given frequencies
    for i in range(len(df.index)):
        key = df.index[i]
        if key in freqDict:
            df.iloc[i] += freqDict[key]
            del freqDict[key]

    # Insert all new keys with given frequencies
    indexes = []
    vals = []
    for key in freqDict:
        indexes.append(key)
        vals.append(freqDict[key])
    
    # Create a new, updated DataFrame
    df = df.append(pd.DataFrame({ headers[1]: vals }, index=indexes)).astype('int32')
    pd.DataFrame.to_csv(df, filePath, index_label=headers[0])