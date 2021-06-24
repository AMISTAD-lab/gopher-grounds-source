import copy
import numpy as np
import time
import geneticAlgorithm.constants as constants
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.library as lib
import misc.csvUtils as csvUtils

cellAlphabet = [x for x in range(93)]

def geneticAlgorithm(cellAlphabet, fitnessFunc, threshold, maxIterations = 10000, showLogs = True, trial = None, export = False, functionName = ''):
    """
    Finds a near-optimal solution in the search space using the given fitness function
    Returns a 3-tuple of (finalPopulation, bestTrap (encoded), bestFitness)
    """
    fitnesses = np.array([0 for _ in range(15)])

    population = []

    # Sampling the (encoded) population until we get one non-zero member
    while(np.count_nonzero(fitnesses) == 0):
        population = lib.initializePopulation(cellAlphabet)
        fitnesses = [fitnessFunc(member) for member in population]
    
    # Recalculate frequencies
    fitnesses = [fitnessFunc(member, updateFreq=True) for member in population]

    generation  = 0
    startTime = lastTime = time.time()

    writeData = [
        [
            trial, generation, trap, functionName,
            round(functions.functionalFitness(trap), 4),
            round(functions.coherentFitness(trap), 4)
        ]
        for trap in population
    ]

    inputPath = f'./frequencies/{functionName}.csv'
    headers = ['Trial', 'Generation', 'Trap', 'Function', 'Lethality', 'Coherence']

    if export:
        csvUtils.updateGenerationFile(inputPath, writeData, headers)
        writeData = []

    while generation < maxIterations:
        if showLogs and (generation % 50 == 0):
            print("Generation {}:".format(generation))
            print("Max fitness\t:", round(max(fitnesses), 3))
            print("Min fitness\t:", round(min(fitnesses), 3))
            print("Mean fitness\t:", round(np.mean(fitnesses), 3))
            print("Median fitness\t:", round(np.median(fitnesses), 3))
            print("Lap Time\t:", round(time.time() - lastTime, 4))
            print("Total Time\t:", round(time.time() - startTime, 4))
            print("------------------------")
            print()
            
            # Set last time
            lastTime = time.time()

        # Creating new population using genetic algorithm
        newPopulation = []
        for _ in range(len(population)):
            parent1, parent2 = lib.selectionFunc(population, fitnesses)
            child = lib.crossoverFunc(parent1, parent2)
            childMutated = lib.mutationFunc(constants.CELL_ALPHABET, child)
            newPopulation.append(childMutated)

        fitnesses = np.array([fitnessFunc(member, updateFreq=True) for member in newPopulation])
        population = newPopulation

        if export:
            for trap in population:
                writeData.append([
                    trial, generation, trap, functionName,
                    round(functions.functionalFitness(trap), 4),
                    round(functions.coherentFitness(trap), 4)
                ])
            
            if generation % 1000 == 0:
                csvUtils.updateGenerationFile(inputPath, writeData, headers)
                writeData = []

        generation += 1

    if export and writeData:
        csvUtils.updateGenerationFile(inputPath, writeData, headers)

    if showLogs:
        print("Generation {}:".format(generation - 1))
        print("Max fitness\t:", round(max(fitnesses), 3))
        print("Min fitness\t:", round(min(fitnesses), 3))
        print("Mean fitness\t:", round(np.mean(fitnesses), 3))
        print("Median fitness\t:", round(np.median(fitnesses), 3))
        print("Lap Time\t:", round(time.time() - lastTime, 4))
        print("Total Time\t:", round(time.time() - startTime, 4))
        print("------------------------")
        print()
    
    optimalIndex = np.where(fitnesses == np.max(fitnesses))[0][0]

    return np.array(population), population[optimalIndex], fitnesses[optimalIndex]
