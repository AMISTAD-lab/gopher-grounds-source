from geneticAlgorithm.analytical import *
import itertools

thickKillProb = [0, 0.15, 0.3, 0.45]
def basicSurviveProb():
    "Return the set of ten possible basic probability of surviving"
    surviveProbSet = set()
    for thickOne in thickKillProb:
        for thinkTwo in thickKillProb:
            surviveProbSet.add(round((1 - thickOne) * (1 - thinkTwo),5))
    return surviveProbSet

def possibleFitness(surviveProbSet, defaultProbEnter = constants.DEFAULT_PROB_ENTER):
    "Return the set of all possible analytical fitness"
    fitnessSet = set()
    theoreticalMax = (1 - 0.55 ** 2) * defaultProbEnter
    timeDist = getProbabilityDistribution(defaultProbEnter)
    permList = [p for p in itertools.product(surviveProbSet, repeat=len(timeDist))]
    for perm in permList:
        sumProb = 0
        for i,dist in enumerate(timeDist):
            sumProb += (1 - perm[i]) * dist
        fitnessSet.add(round(sumProb * defaultProbEnter / theoreticalMax, 10))
    return fitnessSet


surviveProb = basicSurviveProb()
print(surviveProb)
fitnessSet = possibleFitness(surviveProb)
print(sorted(fitnessSet))
print(len(fitnessSet))