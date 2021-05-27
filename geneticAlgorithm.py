import simulation as sim
import classes.Trap as TrapClass
import algorithms as alg
import numpy as np
import random
from encoding import *

# Nick: I am not sure what the sample space is from the encoding, so I am using the ints from 0-56 for testing.
    # The code I wrote does not depend on any particular sample space so no changes should need to be made.
space = [x for x in range(57)]
population = traps

def randomFitness(configuration):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""
    return np.random.random()

def functionalFitness(configuration, numSimulations = 100):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    ## NOTE: Default probability of entering is 0.8 (found in magicVariables.py)
    ## Simulate the trap running numSimulations times
    numberAlive = 0
    hungerLevels = 5
    for hunger in range(hungerLevels):
        for _ in range(int(numSimulations / hungerLevels)):
            numberAlive += int(sim.simulateTrap(TrapClass.Trap(len(configuration[0]), len(configuration), configuration), False, hunger = hunger / 5)[3])

    ## Calculate statistics
    proportion = numberAlive / numSimulations
    stderr = np.sqrt(proportion * (1 - proportion) / numSimulations)

    # upperCI = proportion + 1.96 * stderr
    # lowerCI = proportion - 1.96 * stderr

    # print("Proportion: ", proportion)
    # print("Std Error: ", round(stderr, 3))
    # print("CI: [", round(lowerCI, 3), ", ", round(upperCI, 3), "]")
    return proportion

def coherentFitness(configuration):
    """Assigns a fitness based on the coherence of a given configuration"""
    return alg.getCoherenceValue(TrapClass.Trap(len(configuration[0]), len(configuration), configuration))

def initializePopulation(searchSpace, populationSize):
    """Initializes the population by sampling from the search space"""
    population = []
    for i in range(populationSize):
        member = []
        for j in range(12):
            member.append(np.random.choice(searchSpace))
        print(member)
        population.append(member)
    return np.array(population)

def checkTermination(fitnesses, measure, threshold):
    """Checks termination as a function of the given fitnesses.
       Stops when measure ('all', 'mean', 'median') of fitness meets threshold
    """
    if measure == 'all':
        for i in range(len(fitnesses)):
            if fitnesses[i] < threshold:
                return False
            else:
                continue
        return True
    elif (measure == 'mean' and np.mean(fitnesses) >= threshold) \
        or (measure == 'median' and np.median(fitnesses) >= threshold):
        return True
    elif (measure == 'mean' and np.mean(fitnesses) < threshold) \
        or (measure == 'median' and np.median(fitnesses) < threshold):
        return False
    else:
        raise ValueError('measure must be \'all\', \'mean\', or \'median\'.')

def selectionFunc(population, fitnessFunc):
    """Performs a roulette wheel-style selection process, 
        giving greater weight to members with greater fitnesses"""
    fitnesses = np.array([])
    for member in population:
        fit = fitnessFunc(member)
        fitnesses = np.append(fitnesses, fit)
    sum = np.sum(fitnesses)
    scaledFitnesses = fitnesses / sum
    return random.choices(population, weights=scaledFitnesses, k=len(population))

def crossoverFunc(population):
    """Crosses-over two members of the population to form a new population"""
    encodedPop = listEncoding(population)
    member1_i = random.randrange(0, len(encodedPop), 1)
    member2_i = random.randrange(0, len(encodedPop), 1)
    while member2_i == member1_i:
        member2_i = random.randrange(0, len(encodedPop), 1)
    # cut occurs between (index - 1) and index
    index = random.randrange(1, len(encodedPop[member1_i]), 1)
    left1 = encodedPop[member1_i][:index]
    right1 = encodedPop[member1_i][index:]
    left2 = encodedPop[member2_i][:index]
    right2 = encodedPop[member2_i][index:]
    encodedPop[member1_i]=(np.append(left1, right2))
    encodedPop[member2_i]=(np.append(left2, right1))
    return encodedPop

def mutationFunc(searchSpace, encodedPop):
    """Performs one a single point mutation on a random member of the population"""
    member_i = random.randrange(0, len(encodedPop), 1)
    index = random.randrange(0, len(encodedPop[member_i]), 1)
    # Ensure the flipped tile is not one of the required fixed tiles
    while (index == 4) or (index == 7) or (index == 10):
        index = random.randrange(0, len(encodedPop[member_i]), 1)
    encodedPop[member_i][index] = np.random.choice(searchSpace)
    return encodedPop

def geneticAlgorithm(searchSpace, fitnessFunc, measure, threshold):
    """Finds a near-optimal solution in the search space using the given fitness function"""
    population = initializePopulation(searchSpace, 20)
    fitnesses = [fitnessFunc(member) for member in population]

    while not checkTermination(fitnesses, measure, threshold):
        population = selectionFunc(population, fitnessFunc)
        encodedPop = crossoverFunc(population)
        encodedPop = mutationFunc(searchSpace, encodedPop)
        population = listDecoding(encodedPop)
        fitnesses = fitnessFunc(population)
    return population
