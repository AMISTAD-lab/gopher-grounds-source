import numpy as np
from geneticAlgorithm.encoding import *
import time
from geneticAlgorithm.library import *

cellAlphabet = [x for x in range(93)]

def geneticAlgorithm(cellAlphabet, fitnessFunc, threshold, measure = 'max', maxIterations = 10000,
 showLogs = True, improvedCallback = True, callbackFactor = 0.99):
    """Finds a near-optimal solution in the search space using the given fitness function"""
    fitnesses = np.array([0 for _ in range(15)])

    population = []

    # Sampling the population until we get one non-zero member
    while(np.count_nonzero(fitnesses) == 0):
        population = initializePopulation(cellAlphabet)
        fitnesses = [fitnessFunc(member) for member in population]

    counter  = 0
    startTime = time.time()

    while not checkTermination(fitnesses, measure, threshold) and counter < maxIterations:
        if showLogs and (counter % 50 == 0):
            print("Generation ", counter, ":")
            print("Max fitness: ", round(max(fitnesses), 3))
            print("Min fitness: ", round(min(fitnesses), 3))
            print("Mean fitness: ", round(np.mean(fitnesses), 3))
            print("Median fitness: ", round(np.median(fitnesses), 3))
            print("Time: ", round(time.time() - startTime, 4))
            print("------------------------")
            print()

        # Make a deep copy of the population and fitness to compare with the new generation
        originalPop = copy.deepcopy(population)
        originalFit = copy.deepcopy(fitnesses)

        population = selectionFunc(population, fitnesses)
        
        encodedPop = listEncoding(population)
        encodedPop = crossoverFunc(encodedPop)
        encodedPop = mutationFunc(cellAlphabet, encodedPop)
        
        population = listDecoding(encodedPop)
        
        fitnesses = np.array([fitnessFunc(member) for member in population])

        # Dismisses the new population if its fitness is less than (old pop's fitness * callbackFactor).
        # callbackFactor should be in the interval [0, 1], where 0 is equivalent to having improvedCallback=False.
        if improvedCallback:
            if measure == 'max' and np.max(fitnesses) < callbackFactor * np.max(originalFit):
                population = originalPop
                fitnesses = originalFit
            elif measure == 'mean' and np.mean(fitnesses) < callbackFactor*np.mean(originalFit):
                population = originalPop
                fitnesses = originalFit
            else:
                if np.median(fitnesses) < callbackFactor*np.median(originalFit):
                    population = originalPop
                    fitnesses = originalFit

        counter += 1

    if showLogs:
        print("Generation ", counter, ":")
        print("Max fitness: ", round(max(fitnesses), 3))
        print("Min fitness: ", round(min(fitnesses), 3))
        print("Mean fitness: ", round(np.mean(fitnesses), 3))
        print("Median fitness: ", round(np.median(fitnesses), 3))
        print("Time: ", round(time.time() - startTime, 4))
        print("------------------------")
        print()

    return np.array(population)
