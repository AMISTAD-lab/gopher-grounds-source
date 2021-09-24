from classes.Encoding import Encoding
from classes.GeneticAlgorithm import GeneticAlgorithm

def geneticAlgorithm(functionName, encoder: Encoding, maxGenerations = 10000, showLogs = True, trial = None, barData={}, writer=None):
    """
    Finds a near-optimal solution in the search space using the given fitness function
    Returns a 3-tuple of (finalPopulation, bestTrap (encoded), bestFitness)
    """
    genetic_algorithm = GeneticAlgorithm(encoder=encoder)
    return genetic_algorithm.run(functionName, maxGenerations, showLogs, trial, barData, writer)

