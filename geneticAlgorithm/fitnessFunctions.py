from geneticAlgorithm.cellarray import compareCells
from geneticAlgorithm.encoding import singleEncoding
import numpy as np
import simulation as sim
from geneticAlgorithm.utils import createTrap, zapsGopher
import algorithms as alg

fitnessDic = {}

def randomFitness(_):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""
    return np.random.random()

def functionalFitness(configuration, numSimulations = 5000, printStatistics = False):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    # If the trap does not zap the gopher, then it cannot kill any gophers
    if not zapsGopher(configuration):
        return 0

    # Convert list to string to reference in dictionary
    strEncoding = np.array2string(configuration)

    if strEncoding in fitnessDic:
        return fitnessDic[strEncoding]

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
    
    fitnessDic[strEncoding] = proportion

    return proportion

def coherentFitness(configuration):
    """Assigns a fitness based on the coherence of a given configuration"""
    return alg.getCoherenceValue(createTrap(configuration))

def combinedFitness(configuration):
    """Assigns a fitness based on the coherence AND function of a configuration"""
    memberStr = np.array2string(singleEncoding(configuration))

    if memberStr in fitnessDic:
        return fitnessDic[memberStr]

    coherence = coherentFitness(configuration)
    functionality = functionalFitness(configuration)

    sigmoid = lambda x : 1 / (1 + np.exp(-1 * x))
    evaluator = lambda x, y: sigmoid(np.sum([x, y]) / np.exp(np.abs(x - y)))
    
    # Scale the result to have evaluator(0, 0) = 0 and evaluator(1, 1) = 1
    result = (2 * evaluator(coherence, functionality) - 1) / evaluator(1, 1)

    fitnessDic[memberStr] = result
    
    return result