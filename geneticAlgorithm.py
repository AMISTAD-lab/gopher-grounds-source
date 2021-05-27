import simulation as sim
import classes.Trap as TrapClass
import algorithms as alg
import numpy as np
import random
from encoding import *
import designedTraps

# Nick: I am not sure what the sample space is from the encoding, so I am using the ints from 0-56 for testing.
    # The code I wrote does not depend on any particular sample space so no changes should need to be made.
cellAlphabet = [x for x in range(93)]
population = traps

def randomFitness(_):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""
    return np.random.random()

def functionalFitness(configuration, numSimulations = 100, printStatistics = False):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    # NOTE: Default probability of entering is 0.8 (found in magicVariables.py)
    # Simulate the trap running numSimulations times
    numberAlive = 0
    hungerLevels = 5
    for hunger in range(hungerLevels):
        for _ in range(int(numSimulations / hungerLevels)):
            numberAlive += int(sim.simulateTrap(TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration), False, hunger = hunger / 5)[3])

    # Calculate statistics
    proportion = 1 - numberAlive / numSimulations

    if printStatistics:
        stderr = np.sqrt(proportion * (1 - proportion) / numSimulations)

        upperCI = proportion + 1.96 * stderr
        lowerCI = proportion - 1.96 * stderr

        print("Proportion: ", proportion)
        print("Std Error: ", round(stderr, 3))
        print("CI: [", round(lowerCI, 3), ", ", round(upperCI, 3), "]")

    return proportion

def coherentFitness(configuration):
    """Assigns a fitness based on the coherence of a given configuration"""
    return alg.getCoherenceValue(TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration))

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
                cellCode = 2
            elif i == 10:
                cellCode = 0

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

def selectionFunc(population, fitnesses):
    """Performs a roulette wheel-style selection process, 
        giving greater weight to members with greater fitnesses"""
    # Normalize all fitnesses
    fitnessSum = np.sum(fitnesses)
    scaledFitnesses = fitnesses / fitnessSum if fitnessSum else 0

    return random.choices(population, weights = scaledFitnesses if fitnessSum else None, k=len(population))

def crossoverFunc(encodedPop):
    """Crosses-over two members of the population to form a new population (one-point crossover)"""
    # Get two members to crossover (use index to replace in list at end)
    member1_i = random.randrange(0, len(encodedPop), 1)
    member2_i = random.randrange(0, len(encodedPop), 1)
    while member2_i == member1_i:
        member2_i = random.randrange(0, len(encodedPop), 1)

    # Cut occurs between (index - 1) and index
    index = random.randrange(1, len(encodedPop[member1_i]), 1)

    # Calculate the left and right ends of the new members
    left1 = encodedPop[member1_i][:index]
    right1 = encodedPop[member1_i][index:]
    left2 = encodedPop[member2_i][:index]
    right2 = encodedPop[member2_i][index:]

    # Replace these members in the encoded population
    encodedPop[member1_i]=(np.append(left1, right2))
    encodedPop[member2_i]=(np.append(left2, right1))
    
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

def geneticAlgorithm(cellAlphabet, fitnessFunc, measure, threshold, maxIterations = 1000):
    """Finds a near-optimal solution in the search space using the given fitness function"""
    population = initializePopulation(cellAlphabet, 20)
    fitnesses = np.array([fitnessFunc(member.tolist()) for member in population])

    counter  = 0

    while not checkTermination(fitnesses, measure, threshold) and counter < maxIterations:
        if (counter % 50 == 0):
            print("Generation ", counter, ":")
            print("Max fitness: ", max(fitnesses))
            print("------------------------")
            print()

        population = selectionFunc(population, fitnesses)
        
        encodedPop = listEncoding(population)

        encodedPop = crossoverFunc(encodedPop)
        encodedPop = mutationFunc(cellAlphabet, encodedPop)
        
        population = listDecoding(encodedPop)
        
        fitnesses = np.array([fitnessFunc(member.tolist()) for member in population])

        counter += 1
    return population

geneticAlgorithm(cellAlphabet, coherentFitness, 'mean', 0.8)