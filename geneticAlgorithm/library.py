import numpy as np
import random
from classes.Encoding import Encoding
import geneticAlgorithm.constants as constants

"""
A library of all essential functions for the genetic algorithm
"""
def generateTrap(encoding: Encoding = Encoding()):
    member = []
    for i in range(12):
        cellCode = random.randrange(2, len(constants.CELL_ALPHABET), 1)
        
        # Ensuring the board is valid
        if i == encoding.food:
            cellCode = 1 # Food
        elif i == encoding.floor:
            cellCode = 2 # Floor
        elif i == encoding.door:
            cellCode = 0 # Door

        member.append(cellCode)
    return np.array(member)


def initializePopulation(encoding: Encoding, populationSize = 20):
    """ Initializes the population (encoded as per the encoding) by sampling from the search space """
    if not encoding:
        raise Exception('An encoding object must be given to initializePopulation')

    return np.array([generateTrap(encoding) for _ in range(populationSize)])

def checkTerminationMultiobjective(functionals, coherents, threshold):
    """
        Checks termination as a function of the given fitnesses.
        Stops when measure ('all', 'mean', 'median') of fitness meets threshold
    """
    # Ensure if all fitnesses meet threshold (if we are using this metric)
    # Check if mean or median threshold is met (if we are using either metric)
    if np.max(functionals) < threshold or np.max(coherents) < threshold:
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

def mutationFunc(encoding: Encoding, member):
    """Performs one a single point mutation on the insertee of the new population"""
    # Get the index of the member in the encoded population and the index of the cell to mutate
    index = random.randrange(0, len(member), 1)

    # Ensure the flipped tile is not one of the required fixed tiles
    while index in (encoding.food, encoding.floor, encoding.door):
        index = random.randrange(0, len(member), 1)

    # Change the member of the encoded population and the generated index (not door or food)
    member[index] = constants.CELL_ALPHABET[random.randrange(2, len(constants.CELL_ALPHABET), 1)]

    return np.array(member)