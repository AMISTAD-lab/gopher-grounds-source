from math import *
from typing import Callable, List, Union
import numpy as np
import pandas as pd
import libs.algorithms as alg
import geneticAlgorithm.analytical as analytical
import geneticAlgorithm.constants as constants
from geneticAlgorithm.encoding import singleDecoding, singleEncoding
import geneticAlgorithm.utils as utils

randomFitnesses = {}
functionalFitnesses = {}
coherentFitnesses = {}
combinedFitnesses = {}
binaryDistanceFitnesses = {}
distanceFitneses = {}

# Global target trap
targetTrap = np.array([])

def updateFreqs(strEncoding, freqDict, fofDict):
    ''' Increments the strEncoding freq by 1 and updates all frequencies of frequencies '''
    # Putting in frequencies if not already there
    if strEncoding not in freqDict:
        freqDict[strEncoding] = 0
    
    # Keeping track of old frequency
    oldFreq = freqDict[strEncoding]

    # Updating frequency
    freqDict[strEncoding] += 1

    # Subtracting 1 from old FoF and adding 1 to new FoF
    if oldFreq in fofDict:
        fofDict[oldFreq] -= 1

    if ((oldFreq + 1) not in fofDict):
        fofDict[oldFreq + 1] = 0

    fofDict[oldFreq + 1] += 1

def randomFitness(encodedInput: Union[List[int], np.array, List[List[int]]]):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""   
    ## Prevent duplicate code
    def calcFitness (encoding: List[int]):
        strEncoding = np.array2string(encoding)

        # Returning cached value
        if strEncoding in randomFitnesses:
            return randomFitnesses[strEncoding]

        return np.random.random()
    
    # Return either a single fitness or a list of fitnesses, depending on argument
    if isinstance(encodedInput, np.ndarray) and isinstance(encodedInput[0], (np.int32, np.int64)):
        return calcFitness(encodedInput)

    return np.array([calcFitness(trap) for trap in encodedInput])

def functionalFitness(encodedInput, defaultProbEnter = constants.DEFAULT_PROB_ENTER):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    ## Prevent duplicate code
    def calcFitness(encoding):
        configuration = singleDecoding(encoding)

        # Convert list to string to reference in dictionary
        strEncoding = np.array2string(encoding)

        # Returning cached value if possible
        if strEncoding in functionalFitnesses:
            return functionalFitnesses[strEncoding]

        # This is the max probability of killing a gopher 
        theoreticalMax = (1 - 0.55 ** 2) * defaultProbEnter

        # NOTE: Default probability of entering is 0.8 (found in magicVariables.py)
        fitness = analytical.trapLethality(configuration, defaultProbEnter) / theoreticalMax

        functionalFitnesses[strEncoding] = fitness
        
        return fitness

    # Return either a single fitness or a list of fitnesses, depending on argument
    if isinstance(encodedInput, np.ndarray) and isinstance(encodedInput[0], (np.int32, np.int64)):
        return calcFitness(encodedInput)

    return np.array([calcFitness(trap) for trap in encodedInput])

def coherentFitness(encodedInput):
    """Assigns a fitness based on the coherence of a given configuration"""
    ## Prevent duplicate code
    def calcFitness(encoding):
        configuration = singleDecoding(encoding)

        # Convert list to string to reference in dictionary
        strEncoding = np.array2string(encoding)

        if strEncoding in coherentFitnesses:
            return coherentFitnesses[strEncoding]

        fitness = alg.getCoherenceValue(utils.createTrap(configuration))
        coherentFitnesses[strEncoding] = fitness

        return fitness
    
    # Return either a single fitness or a list of fitnesses, depending on argument
    if isinstance(encodedInput, np.ndarray) and isinstance(encodedInput[0], (np.int32, np.int64)):
        return calcFitness(encodedInput)

    return np.array([calcFitness(trap) for trap in encodedInput])

def combinedFitness(encodedInput):
    """Assigns a fitness based on the coherence AND function of a configuration"""

    def calcFitness(encoded):
        # Convert list to string to reference in dictionary
        strEncoding = np.array2string(encoded)

        if strEncoding in combinedFitnesses:
            return combinedFitnesses[strEncoding]

        MAX_DIFF = 0.2

        coherence = coherentFitness(encoded)
        functionality = functionalFitness(encoded)

        sigmoid = lambda x : 1 / (1 + np.exp(-1 * x))
        evaluator = lambda x, y: sigmoid(np.sum([x, y]) / np.exp(2 * np.abs(x - y)))
        
        # Scale the result to have combinedFitness(0, 0) = 0 and combinedFitness(1, 1) = 1
        fitness = (2 * evaluator(coherence, functionality) - 1) / (2 * evaluator(1, 1) - 1)

        # If the difference is too large, then penalize the fitness
        if (np.abs(functionality - coherence) > MAX_DIFF):
            fitness /= 2

        combinedFitnesses[strEncoding] = fitness

        return fitness
    
    # Return either a single fitness or a list of fitnesses, depending on argument
    if isinstance(encodedInput, np.ndarray) and isinstance(encodedInput[0], (np.int32, np.int64)):
        return calcFitness(encodedInput)

    return np.array([calcFitness(trap) for trap in encodedInput])

def binaryDistanceFitness(encodedInput):
    """Assigns a fitness based on the binary distance to the target configuration"""
    def calcFitness(encoding):
        # Convert list to string to reference in dictionary
        strEncoding = np.array2string(encoding)

        if strEncoding in binaryDistanceFitnesses:
            return binaryDistanceFitnesses[strEncoding]

        numDiff = 0.0
        for i in range(len(encoding)):
            if encoding[i] != targetTrap[i]:
                numDiff += 1

        return 1 - (numDiff / (len(encoding) - 3))

    # Return either a single fitness or a list of fitnesses, depending on argument
    if isinstance(encodedInput, np.ndarray) and isinstance(encodedInput[0], (np.int32, np.int64)):
        return calcFitness(encodedInput)

    return np.array([calcFitness(trap) for trap in encodedInput])

# TODO: Fix this function
# def distanceFitness(configuration, targetTrap):
#     """Assigns a fitness based on the distance to the target configuration"""
#     encodedTarget = singleEncoding(targetTrap)
#     # Convert list to string to reference in dictionary
#     encoding = singleEncoding(configuration)
#     strEncoding = np.array2string(encoding)

#     # Maintain frequency dictionary
#     if strEncoding not in binaryDistanceFreqs:
#         binaryDistanceFreqs[strEncoding] = 0
    
#     binaryDistanceFreqs[strEncoding] += 1

#     if strEncoding in binaryDistanceFitnesses:
#         return binaryDistanceFitnesses[strEncoding]

#     distance = 0
#     for i in range(len(encoding)):
#         if encoding[i] != encodedTarget[i]:
#             distance += 1

#     return distance / (len(encoding) - 3)

def multiobjectiveFitness(population, defaultProbEnter = constants.DEFAULT_PROB_ENTER):
    """
    Given a list of traps, calculate the multiobjective (coherence and functional) fitness for each.
    Returns an 1 x n numpy array [multifitness] * combinedFitness(config_maxScore) in order of population list
    """

    # Return the combined fitness if one trap is passed in
    if isinstance(population[0], (np.int32, np.int64)):
        return combinedFitness(population)
    
    # create preliminary variables
    size = len(population)
    functionals = []
    coherents = []
    scores = np.empty((0,1), int)

    # determine score of trap by number of other traps it dominates
    for trap in population:
        functionals.append(functionalFitness(trap, defaultProbEnter))
        coherents.append(coherentFitness(trap))

    data = {"functional fitness": functionals, "coherent fitness": coherents}
    df = pd.DataFrame(data, columns = ["functional fitness", "coherent fitness"])

    for i in range(size):
        score = 0
        for j in range(size):
            if df.loc[i, "functional fitness"] >= df.loc[j, "functional fitness"] \
                and df.loc[i, "coherent fitness"] >= df.loc[j, "coherent fitness"]:
                score += 1
        scores = np.append(scores, score)

    # boost score of a trap depending on how far away it is from other traps of same score (farther is better)
    # each score booster is in the interval [0,1]
    boosters = [0 for x in range(size)]
    posScores = np.unique(scores)
    for score in posScores:
        score_i = []
        for i in range(size):
            if scores[i] == score:
                score_i.append(i)
        for i in score_i:
            distList = []
            if len(score_i) == 1:
                minDist = sqrt(2)   # sqrt(2) is the maximum possible distance between to points in unit square
            else:
                for j in score_i:
                    if i != j:
                        distList.append(dist([df.loc[i, "functional fitness"],df.loc[i, "coherent fitness"]],
                        [df.loc[j, "functional fitness"],df.loc[j, "coherent fitness"]]))
                minDist = min(distList)
            boosters[i] += minDist/sqrt(2)
    newScores = [scores[i] + boosters[i] for i in range(size)]
    newScores = [newScores[i]/max(newScores) for i in range(size)]

    return np.array(newScores) * combinedFitness(population[np.argmax(newScores)])

functionLut = {
    'random': randomFitness,
    'functional': functionalFitness,
    'cohernece': coherentFitness,
    'multiobjective': multiobjectiveFitness,
    'binary-distance': binaryDistanceFitness,
}

def getFunctionFromName(functionName: str) -> Callable:
    """Takes in a function name, returns the corresponding fitness function"""
    return functionLut[functionName]

