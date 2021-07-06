from geneticAlgorithm.analytical import *

thickKillProb = [0, 0.15, 0.3, 0.45]
def basicSurviveProb():
    "Return the set of ten possible basic probability of surviving"
    surviveProbSet = set()
    for thickOne in thickKillProb:
        for thinkTwo in thickKillProb:
            surviveProbSet.add((1 - thickOne) * (1 - thinkTwo))
    return surviveProbSet

def possibleFitness(surviveProbSet, defaultProbEnter = constants.DEFAULT_PROB_ENTER):
    "Return the set of all possible analytical fitness"
    fitnessSet = set()
    theoreticalMax = (1 - 0.55 ** 2) * defaultProbEnter
    timeDist = getProbabilityDistribution(defaultProbEnter)
    for surviveProb in surviveProbSet:
        sumProb = 0.0
        for dist in timeDist:
            sumProb += (1 - surviveProb) * dist
        fitnessSet.add(sumProb * defaultProbEnter / theoreticalMax)
    return fitnessSet


surviveProb = basicSurviveProb()
fitnessSet = possibleFitness(surviveProb)
print(fitnessSet)
print(len(fitnessSet))