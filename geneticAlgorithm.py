import simulation as sim
import classes.Trap as TrapClass
import algorithms as alg
import numpy as np
import random
from encoding import *
import visualize as vis
import os
import webbrowser
import time

functionDic = {}

cellAlphabet = [x for x in range(93)]
population = traps

def createTrap(configuration):
    """Takes in a board configuration and wraps that configuration in a trap class"""
    return TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration)

def randomFitness(_):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""
    return np.random.random()

def functionalFitness(configuration, numSimulations = 100, printStatistics = False):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    # Convert list to string to reference in dictionary
    strEncoding = np.array2string(configuration)

    if strEncoding in functionDic:
        return functionDic[strEncoding]

    # NOTE: Default probability of entering is 0.8 (found in magicVariables.py)
    # Simulate the trap running numSimulations times
    numberAlive = 0
    hungerLevels = 5
    for hunger in range(hungerLevels):
        for _ in range(int(numSimulations / hungerLevels)):
            numberAlive += int(sim.simulateTrap(createTrap(configuration), False, hunger = hunger / 5)[3])

    # Calculate statistics
    proportion = 1 - numberAlive / numSimulations

    if printStatistics:
        stderr = np.sqrt(proportion * (1 - proportion) / numSimulations)

        upperCI = proportion + 1.96 * stderr
        lowerCI = proportion - 1.96 * stderr

        print("Proportion: ", proportion)
        print("Std Error: ", round(stderr, 3))
        print("CI: [", round(lowerCI, 3), ", ", round(upperCI, 3), "]")
    
    functionDic[strEncoding] = proportion

    return proportion

def coherentFitness(configuration):
    """Assigns a fitness based on the coherence of a given configuration"""
    return alg.getCoherenceValue(createTrap(configuration))

def initializePopulation(cellAlphabet, populationSize = 20):
    """Initializes the population by sampling from the search space"""
    population = []
    for _ in range(populationSize):
        # Temporary variable to store configuration as it is generated
        member = []
        for i in range(12):
            cellCode = random.randrange(2, len(cellAlphabet), 1)
            
            # Ensuring the board is valid
            if i == 4:
                cellCode = 1 # Food
            elif i == 7:
                cellCode = 2 # Floor
            elif i == 10:
                cellCode = 0 # Door

            member.append(cellCode)

        population.append(member)

    return listDecoding(population)

def checkTermination(fitnesses, measure, threshold):
    """Checks termination as a function of the given fitnesses.
       Stops when measure ('all', 'mean', 'median') of fitness meets threshold
    """
    if (measure not in ['all', 'mean', 'median']):
        raise ValueError('measure must be \'all\', \'mean\', or \'median\'.')

    # Ensure if all fitnesses meet threshold (if we are using this metric)
    if measure == 'all':
        for i in range(len(fitnesses)):
            if fitnesses[i] < threshold:
                return False

    # Check if mean or median threshold is met (if we are using either metric)
    elif (measure == 'mean' and np.mean(fitnesses) < threshold) \
        or (measure == 'median' and np.median(fitnesses) < threshold):
        return False

    # If we get to this part, then all thresholds are met, and we can terminate
    return True

def selectionFunc(population, fitnesses, elitism = False):
    """Performs a roulette wheel-style selection process, 
        giving greater weight to members with greater fitnesses"""
    # "Normalize" all fitnesses such that they sum to 1
    fitnessSum = np.sum(fitnesses)
    scaledFitnesses = fitnesses / fitnessSum if fitnessSum else 0 * fitnesses
    newPopulation = random.choices(
        population,
        weights = scaledFitnesses if fitnessSum else None,
        k=(len(population) - 2) if elitism else len(population)
    )
    
    if elitism:
        # Keep the individuals with the two highest fitnesses for the next generation
        index1 = np.argmax(scaledFitnesses)
        index2 = 0
        for i in range(len(scaledFitnesses)):
            if i != index1 and scaledFitnesses[index2] < scaledFitnesses[i]:
                index2 = i
        newPopulation.append(population[index1])
        newPopulation.append(population[index2])

    return newPopulation

def crossoverFunc(encodedPop, debug = False):
    """Crosses-over two members of the population to form a new population (one-point crossover)"""
    # Get two members to crossover (use index to replace in list at end)
    member1_i = random.randrange(0, len(encodedPop), 1)
    member2_i = random.randrange(0, len(encodedPop), 1)
    
    if debug:
        print("original:")
        print(encodedPop[member1_i])
        print(encodedPop[member2_i])
        print()
    
    while member1_i == member2_i:
        member2_i = random.randrange(0, len(encodedPop), 1)

    # Cut occurs between (index - 1) and index
    index = random.randrange(1, len(encodedPop[member1_i]), 1)
    if debug:
        print("index:")
        print(index)
        print()

    # Calculate the left and right ends of the new members
    left1 = encodedPop[member1_i][:index]
    right1 = encodedPop[member1_i][index:]
    left2 = encodedPop[member2_i][:index]
    right2 = encodedPop[member2_i][index:]

    if debug:
        print("parts:")
        print(left1, right1)
        print(left2, right2)
        print()

    # Need to allocate arrays before-hand to prevent really weird error
    # Error mutates encodedPop[member1_i] but not encodedPop[member2_i]
    firstList = np.append(left1, right2)
    secondList = np.append(left2, right1)

    # Replace these members in the encoded population
    encodedPop[member1_i] = firstList
    encodedPop[member2_i] = secondList
    
    if debug:
        print("is:")
        print(encodedPop[member1_i])
        print(encodedPop[member2_i])

    return encodedPop

def mutationFunc(cellAlphabet, encodedPop):
    """Performs one a single point mutation on a random member of the population"""
    # Get the index of the member in the encoded population and the index of the cell to mutate
    member_i = random.randrange(0, len(encodedPop), 1)
    index = random.randrange(0, len(encodedPop[member_i]), 1)

    # Ensure the flipped tile is not one of the required fixed tiles
    while (index == 4) or (index == 7) or (index == 10):
        index = random.randrange(0, len(encodedPop[member_i]), 1)

    # Change the member of the encoded population and the generated index (not door or food)
    encodedPop[member_i][index] = cellAlphabet[random.randrange(2, len(cellAlphabet), 1)]
    return encodedPop

def geneticAlgorithm(cellAlphabet, fitnessFunc, measure, threshold, maxIterations = 10000,
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
            if measure == 'mean' and np.mean(fitnesses) < callbackFactor*np.mean(originalFit):
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

def exportGeneticOutput(outputFile, cellAlphabet, fitnessFunc, measure, threshold, maxIterations = 10000, showLogs = True):
    """
    Runs the genetic algorithm with the given parameters and writes a new file with the list encodings in it (to preserve the output)
    """
    finalPopulation = geneticAlgorithm(cellAlphabet, fitnessFunc, measure, threshold, maxIterations, showLogs)
    with open(outputFile, 'w') as out:
        for i, member in enumerate(listEncoding(finalPopulation)):
            out.write(str(i) + ": ")
            
            # Standardize spacing
            if i < 10:
                out.write(" ")

            out.write("[")
            
            # Write in array form
            for j, digit in enumerate(member):
                out.write(str(digit))
                
                if j < len(member) - 1:
                    out.write(', ')
            
            out.write(']')
            out.write('\n')

def simulateTrapInBrowser(listEncoding):
    """Takes in a list encoding and simulates the trap in the browser"""
    decodedList = singleDecoding(listEncoding)
    simulationInfo = sim.simulateTrap(createTrap(decodedList), False)[:3]
    vis.writeTojs([simulationInfo], False)

    # opens the animation in the web browser
    webbrowser.open_new_tab('file://' + os.path.realpath('./animation/animation.html'))

# exportGeneticOutput('geneticAlgorithm.txt', cellAlphabet, functionalFitness, 'median', 0.6)
simulateTrapInBrowser([42, 13, 50, 81, 1, 17, 85, 2, 25, 44, 0, 26])