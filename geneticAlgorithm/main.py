import numpy as np
import time
from classes.Encoding import Encoding
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.library as lib

def geneticAlgorithm(functionName, encoder: Encoding, maxGenerations = 10000, showLogs = True, trial = None, barData={}, writer=None):
    """
    Finds a near-optimal solution in the search space using the given fitness function
    Returns a 3-tuple of (finalPopulation, bestTrap (encoded), bestFitness)
    """
    fitnessFunc = functions.getFunctionFromName(functionName)
    fitnesses = np.array(20 * [0])
    population = np.array([])

    if functionName == 'binary-distance':
        functions.targetTrap = lib.generateTrap(encoder)

    # Destructure population into CSV format
    getWriteData = lambda population, fitnesses : [
            [
                trial, generation, trap, functionName,
                round(fitnesses[i], 4),
                round(functions.getLethality(trap, encoder), 4),
                round(functions.getCoherence(trap, encoder), 4),
                round(functions.getCombined(trap, encoder), 4),
            ]
            for i, trap in enumerate(population)
        ]

    # Sampling the (encoded) population until we get one non-zero member
    while(np.count_nonzero(fitnesses) == 0):
        population = lib.initializePopulation(encoder)
        fitnesses = fitnessFunc(population, encoder)
    
    # Recalculate frequencies
    fitnesses = fitnessFunc(population, encoder)

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
            print(f"Generation {generation}:")
            print("Current Max fitness\t: {}".format(round(max(fitnesses), 3)))
            print("Global Max fitness\t: {}".format(round(maxFitness, 3)))
            print("Lap Time\t\t: {}".format(round(time.time() - lastTime, 4)))
            print("Total Time\t\t: {}".format(round(time.time() - startTime, 4)))
            print("------------------------")
            print()
            
            # Set last time
            lastTime = time.time()

        # Creating new population using genetic algorithm
        newPopulation = []
        for _ in range(len(population)):
            parent1, parent2 = lib.selectionFunc(population, fitnesses)
            child = lib.crossoverFunc(parent1, parent2)
            childMutated = lib.mutationFunc(encoder, child)
            newPopulation.append(childMutated)

        # Calculating new fitnesses and updating the optimal solutions
        fitnesses = fitnessFunc(newPopulation, encoder)
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
        print(f"Generation {generation}:")
        print("Current Max fitness\t: {}".format(round(max(fitnesses), 3)))
        print("Global Max fitness\t: {}".format(round(maxFitness, 3)))
        print("Lap Time\t\t: {}".format(round(time.time() - lastTime, 4)))
        print("Total Time\t\t: {}".format(round(time.time() - startTime, 4)))
        print("------------------------")
        print()

    return np.array(population), bestTrap, maxFitness
