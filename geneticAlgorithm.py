def randomFitness(configuration):
    """Assigns a random fitness to each configuration (choosing uniformly at random)"""
    pass

def functionalFitness(configuration):
    """
    Assigns a fitness based on the function of the given configuration.
    To do so, we run simulations to get a confidence interval on whether the gopher dies or not.
    """
    pass

def coherentFitness(configuration):
    """Assigns a fitness based on the coherence of a given configuration"""
    pass

def initializePopulation(searchSpace, populationSize):
    """Initializes the population by sampling from the search space"""
    pass

def checkTermination(fitnesses):
    """checks termination as a function of the given fitnesses"""
    pass

def selectionFunc(population):
    """takes a sample from the population to replicate from"""
    pass

def recombinationFunc(population):
    """recombines members of the population to form a new population"""
    pass

def mutationFunc(population):
    """mutates members of the population at random to introduce genetic diversity"""
    pass

def geneticAlgorithm(searchSpace, fitnessFunc):
    """finds a near-optimal solution in the search space using the given fitness function"""
    population = initializePopulation(searchSpace, 20)
    fitnesses = [fitnessFunc(individual) for individual in population]

    while not checkTermination(fitnesses):
        population = selectionFunc(population)
        population = recombinationFunc(population)
        population = mutationFunc(population)

        fitnesses = fitnessFunc(population)
    pass
