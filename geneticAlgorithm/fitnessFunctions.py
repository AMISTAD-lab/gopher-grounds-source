import numpy as np
import algorithms as alg
import geneticAlgorithm.analytical as analytical
import geneticAlgorithm.constants as constants
from geneticAlgorithm.encoding import singleEncoding
from geneticAlgorithm.utils import createTrap

functionalFitnesses = {}
coherentFitnesses = {}
combinedFitnesses = {}

def randomFitness(_):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""
    return np.random.random()

def functionalFitness(configuration, defaultProbEnter = constants.DEFAULT_PROB_ENTER):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    # Convert list to string to reference in dictionary
    encoding = singleEncoding(configuration)
    strEncoding = np.array2string(encoding)

    if strEncoding in functionalFitnesses:
        return functionalFitnesses[strEncoding]

    # This is the max probability of killing a gopher 
    theoreticalMax = (1 - 0.55 ** 2) * defaultProbEnter

    # NOTE: Default probability of entering is 0.8 (found in magicVariables.py)
    fitness = analytical.trapLethality(configuration, defaultProbEnter) / theoreticalMax

    functionalFitnesses[strEncoding] = fitness
    return fitness

def coherentFitness(configuration):
    """Assigns a fitness based on the coherence of a given configuration"""
    # Convert list to string to reference in dictionary
    encoding = singleEncoding(configuration)
    strEncoding = np.array2string(encoding)

    if strEncoding in coherentFitnesses:
        return coherentFitnesses[strEncoding]

    fitness = alg.getCoherenceValue(createTrap(configuration))
    coherentFitnesses[strEncoding] = fitness

    return fitness

def combinedFitness(configuration):
    """Assigns a fitness based on the coherence AND function of a configuration"""
    # Convert list to string to reference in dictionary
    encoding = singleEncoding(configuration)
    strEncoding = np.array2string(encoding)

    if strEncoding in combinedFitnesses:
        return combinedFitnesses[strEncoding]

    coherence = coherentFitness(configuration)
    functionality = functionalFitness(configuration)

    sigmoid = lambda x : 1 / (1 + np.exp(-1 * x))
    evaluator = lambda x, y: sigmoid(np.sum([x, y]) / np.exp(np.abs(x - y)))
    
    # Scale the result to have combinedFitness(0, 0) = 0 and combinedFitness(1, 1) = 1
    result = (2 * evaluator(coherence, functionality) - 1) / (2 * evaluator(1, 1) - 1)

    combinedFitnesses[strEncoding] = result
    
    return result