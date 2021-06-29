from typing import List, Union
import numpy as np
import libs.algorithms as alg
import geneticAlgorithm.analytical as analytical
import geneticAlgorithm.constants as constants
from geneticAlgorithm.encoding import singleDecoding, singleEncoding
from geneticAlgorithm.utils import createTrap

randomFoF = {}
functionalFoF = {}
coherentFoF = {}
combinedFoF = {}

randomFitnesses = {}
functionalFitnesses = {}
coherentFitnesses = {}
combinedFitnesses = {}
binaryDistanceFitnesses = {}
distanceFitneses = {}

randomFreqs = {}
functionalFreqs = {}
coherentFreqs = {}
combinedFreqs = {}
binaryDistanceFreqs = {}
distanceFreqs = {}

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

def randomFitness(encodedInput: Union[List[int], np.array, List[List[int]]], updateFreq=False):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""   
    ## Prevent duplicate code
    def calcFitness (encoding: List[int], updateFreq = False):
        strEncoding = np.array2string(encoding)

        if updateFreq:
            updateFreqs(strEncoding, randomFreqs, randomFoF)

        # Returning cached value
        if strEncoding in randomFitnesses:
            return randomFitnesses[strEncoding]

        return np.random.random()
    
    # Return either a single fitness or a list of fitnesses, depending on argument
    if isinstance(encodedInput, np.ndarray) and isinstance(encodedInput[0], (np.int32, np.int64)):
        return calcFitness(encodedInput, updateFreq)

    return np.array([calcFitness(trap, updateFreq) for trap in encodedInput])

def functionalFitness(encodedInput, defaultProbEnter = constants.DEFAULT_PROB_ENTER, updateFreq=False):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    ## Prevent duplicate code
    def calcFitness(encoding, updateFreq=False):
        configuration = singleDecoding(encoding)

        # Convert list to string to reference in dictionary
        strEncoding = np.array2string(encoding)

        if updateFreq:
            updateFreqs(strEncoding, functionalFreqs, functionalFoF)

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
        return calcFitness(encodedInput, updateFreq)

    return np.array([calcFitness(trap, updateFreq) for trap in encodedInput])

def coherentFitness(encodedInput, updateFreq=False):
    """Assigns a fitness based on the coherence of a given configuration"""
    ## Prevent duplicate code
    def calcFitness(encoding, updateFreq=False):
        configuration = singleDecoding(encoding)

        # Convert list to string to reference in dictionary
        strEncoding = np.array2string(encoding)
        
        if updateFreq:
            updateFreqs(strEncoding, coherentFreqs, coherentFoF)

        if strEncoding in coherentFitnesses:
            return coherentFitnesses[strEncoding]

        fitness = alg.getCoherenceValue(createTrap(configuration))
        coherentFitnesses[strEncoding] = fitness

        return fitness
    
    # Return either a single fitness or a list of fitnesses, depending on argument
    if isinstance(encodedInput, np.ndarray) and isinstance(encodedInput[0], (np.int32, np.int64)):
        return calcFitness(encodedInput, updateFreq)

    return np.array([calcFitness(trap, updateFreq) for trap in encodedInput])

def combinedFitness(encodedInput, updateFreq=False):
    """Assigns a fitness based on the coherence AND function of a configuration"""

    def calcFitness(encoded, updateFreq=False):
        # Convert list to string to reference in dictionary
        strEncoding = np.array2string(encoded)
        
        if updateFreq:
            updateFreqs(strEncoding, combinedFreqs, combinedFoF)

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
    if isinstance(encodedInput, np.ndarray) and isinstance(encodedInput[0], (np.int32, (np.int32, np.int64))):
        return calcFitness(encodedInput, updateFreq)

    return np.array([calcFitness(trap, updateFreq) for trap in encodedInput])

def binaryDistanceFitness(configuration, targetTrap):
    """Assigns a fitness based on the binary distance to the target configuration"""
    encodedTarget = singleEncoding(targetTrap)
    # Convert list to string to reference in dictionary
    encoding = singleEncoding(configuration)
    strEncoding = np.array2string(encoding)

    # Maintain frequency dictionary
    if strEncoding not in binaryDistanceFreqs:
        binaryDistanceFreqs[strEncoding] = 0
    
    binaryDistanceFreqs[strEncoding] += 1

    if strEncoding in binaryDistanceFitnesses:
        return binaryDistanceFitnesses[strEncoding]

    numDiff = 0.0
    for i in range(len(encoding)):
        if encoding[i] != encodedTarget[i]:
            numDiff += 1

    return numDiff/(len(encoding) - 3)

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
