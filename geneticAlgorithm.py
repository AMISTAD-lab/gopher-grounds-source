import simulation as sim
import classes.Trap as TrapClass
import algorithms as alg
import numpy as np

def randomFitness(configuration):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""
    return np.random.random()

def functionalFitness(configuration, numSimulations = 100):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not 
    or compute the the given configuration's probability of killing a gopher
    """
    ## NOTE: Default probability of entering is 0.8 (found in magicVariables.py)
    ## Simulate the trap running numSimulations times
    numberAlive = 0
    hungerLevels = 5
    for hunger in range(hungerLevels):
        for _ in range(int(numSimulations / hungerLevels)):
            numberAlive += int(sim.simulateTrap(TrapClass.Trap(len(configuration[0]), len(configuration), configuration), False, hunger = hunger / 5)[3])

    ## Calculate statistics
    proportion = numberAlive / numSimulations
    stderr = np.sqrt(proportion * (1 - proportion) / numSimulations)

    upperCI = proportion + 1.96 * stderr
    lowerCI = proportion - 1.96 * stderr

    print("Proportion: ", proportion)
    print("Std Error: ", round(stderr, 3))
    print("CI: [", round(lowerCI, 3), ", ", round(upperCI, 3), "]")
    return proportion

def coherentFitness(configuration):
    """Assigns a fitness based on the coherence of a given configuration"""
    return alg.getCoherenceValue(TrapClass.Trap(len(configuration[0]), len(configuration), configuration))

def initializePopulation(searchSpace, populationSize):
    """Initializes the population by sampling from the search space"""
    pass

def checkTermination(fitnesses):
    """Checks termination as a function of the given fitnesses"""
    pass

def selectionFunc(population):
    """Takes a sample from the population to replicate from"""
    pass

def recombinationFunc(population):
    """Recombines members of the population to form a new population"""
    pass

def mutationFunc(population):
    """Mutates members of the population at random to introduce genetic diversity"""
    pass

def geneticAlgorithm(searchSpace, fitnessFunc):
    """Finds a near-optimal solution in the search space using the given fitness function"""
    population = initializePopulation(searchSpace, 20)
    fitnesses = [fitnessFunc(individual) for individual in population]

    while not checkTermination(fitnesses):
        population = selectionFunc(population)
        population = recombinationFunc(population)
        population = mutationFunc(population)

        fitnesses = fitnessFunc(population)
    pass
