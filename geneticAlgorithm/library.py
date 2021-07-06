import numpy as np
import random
import geneticAlgorithm.encoding as encoding
import geneticAlgorithm.constants as constants

"""
A library of all essential functions for the genetic algorithm
"""
def generateTrap():
    member = []
    for i in range(12):
        cellCode = random.randrange(2, len(constants.CELL_ALPHABET), 1)
        
        # Ensuring the board is valid
        if i == 4:
            cellCode = 1 # Food
        elif i == 7:
            cellCode = 2 # Floor
        elif i == 10:
            cellCode = 0 # Door

        member.append(cellCode)
    return np.array(member)


def initializePopulation(populationSize = 20):
    """ Initializes the population by sampling from the search space """
    population = []
    for _ in range(populationSize):
        # Temporary variable to store configuration as it is generated
        member = []
        for i in range(12):
            cellCode = random.randrange(2, len(constants.CELL_ALPHABET), 1)
            
            # Ensuring the board is valid
            if i == 4:
                cellCode = 1 # Food
            elif i == 7:
                cellCode = 2 # Floor
            elif i == 10:
                cellCode = 0 # Door

            member.append(cellCode)

        population.append(member)

    return np.array(population)

def checkTerminationMultiobjective(functionals, coherents, measure, threshold):
    """Checks termination as a function of the given fitnesses.
       Stops when measure ('all', 'mean', 'median') of fitness meets threshold
    """
    if (measure not in ['all', 'mean', 'median', 'max']):
        raise ValueError('measure must be \'all\', \'mean\', \'median\', or \'max\'.')

    # Ensure if all fitnesses meet threshold (if we are using this metric)
    if measure == 'all':
        for i in range(len(functionals)):
            if functionals[i] < threshold or coherents[i] < threshold:
                return False

    # Check if mean or median threshold is met (if we are using either metric)
    elif (measure == 'mean' and (np.mean(functionals) < threshold or np.mean(coherents) < threshold)) \
        or (measure == 'median' and (np.median(functionals) < threshold or np.median(coherents) < threshold)) \
            or (measure == 'max' and (np.max(functionals) < threshold or np.max(coherents) < threshold)):
        return False

    # If we get to this part, then all thresholds are met, and we can terminate
    return True

def selectionFunc(population, fitnesses, numSelected = 2):
    """
    Performs a roulette wheel-style selection process, giving greater weight to members with greater fitnesses.
    Returns two members from the current population
    """
    # "Normalize" all fitnesses such that they sum to 1
    fitnessSum = np.sum(fitnesses)
    scaledFitnesses = fitnesses / fitnessSum if fitnessSum else 0 * fitnesses
    chosenMembers = random.choices(
        population,
        weights = scaledFitnesses if fitnessSum else None,
        k = numSelected
    )

    return np.array(chosenMembers)

def crossoverFunc(member1, member2):
    """Crosses-over two members to form a new member"""
    # Cut occurs between (index - 1) and index
    index = random.randrange(1, len(member1), 1)

    # Calculate the left and right ends of the new members
    return np.append(member1[:index], member2[index:])

def mutationFunc(member):
    """Performs one a single point mutation on the insertee of the new population"""
    # Get the index of the member in the encoded population and the index of the cell to mutate
    index = random.randrange(0, len(member), 1)

    # Ensure the flipped tile is not one of the required fixed tiles
    while (index == 4) or (index == 7) or (index == 10):
        index = random.randrange(0, len(member), 1)

    # Change the member of the encoded population and the generated index (not door or food)
    member[index] = constants.CELL_ALPHABET[random.randrange(2, len(constants.CELL_ALPHABET), 1)]

    return np.array(member)