import csv
import numpy as np
import os
import time
import geneticAlgorithm.constants as constants
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.library as lib
import misc.csvUtils as csvUtils

cellAlphabet = [x for x in range(93)]

def geneticAlgorithm(cellAlphabet, fitnessFunc, threshold, maxGenerations = 10000, showLogs = True, trial = None, functionName = '', barData={}, writer=None):
    """
    Finds a near-optimal solution in the search space using the given fitness function
    Returns a 3-tuple of (finalPopulation, bestTrap (encoded), bestFitness)
    """
    fitnesses = np.array([0 for _ in range(15)])

    population = []

    # Destructure population into CSV format
    getWriteData = lambda population, fitnesses : [
            [
                trial, generation, trap, functionName,
                round(fitnesses[i]),
                round(functions.functionalFitness(trap), 4),
                round(functions.coherentFitness(trap), 4),
                round(functions.combinedFitness(trap), 4),
            ]
            for i, trap in enumerate(population)
        ]

    # Sampling the (encoded) population until we get one non-zero member
    while(np.count_nonzero(fitnesses) == 0):
        population = lib.initializePopulation(cellAlphabet)
        fitnesses = fitnessFunc(population)
    
    # Recalculate frequencies
    fitnesses = fitnessFunc(population, updateFreq=True)

    generation = 0
    startTime = lastTime = time.time()

    writeData = getWriteData(population, fitnesses)

    currMax = np.argmax(fitnesses)
    maxFitness, bestTrap = fitnesses[currMax], population[currMax]

    while generation < maxGenerations:
        # Write frequency data before we change the population
        if writer and generation % 1000 == 0:
            writer.writerows(writeData)
            writeData = []

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

        # Calculating new fitnesses and updating the optimal solutions
        fitnesses = fitnessFunc(newPopulation, updateFreq = True)
        population = newPopulation

        currMax = np.argmax(fitnesses)
        if fitnesses[currMax] > maxFitness:
            maxFitness = fitnesses[currMax]
            bestTrap = newPopulation[currMax]

        generation += 1

        # Add new data to the writeData list
        if writer:
            writeData.extend(getWriteData(population, fitnesses))

        if barData:
            barData['counter'] += 1

            numBars, maxSteps = barData['numBars'], barData['maxSteps']
            modulo = maxSteps // numBars if numBars <= maxSteps else 1
            
            if barData['counter'] % modulo == 0:
                barData['bar'].next(n=max(1, numBars / maxSteps))

    if writer and writeData:
        writer.writerows(writeData)

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

    return np.array(population), bestTrap, maxFitness
