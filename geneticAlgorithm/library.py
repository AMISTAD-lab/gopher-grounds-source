import random
from geneticAlgorithm.encoding import *

"""
A library of all essential functions for the genetic algorithm
"""

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
    if (measure not in ['all', 'mean', 'median', 'max']):
        raise ValueError('measure must be \'all\', \'mean\', \'median\', or \'max\'.')

    # Ensure if all fitnesses meet threshold (if we are using this metric)
    if measure == 'all':
        for i in range(len(fitnesses)):
            if fitnesses[i] < threshold:
                return False

    # Check if mean or median threshold is met (if we are using either metric)
    elif (measure == 'mean' and np.mean(fitnesses) < threshold) \
        or (measure == 'median' and np.median(fitnesses) < threshold) \
            or (measure == 'max' and np.max(fitnesses) < threshold):
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