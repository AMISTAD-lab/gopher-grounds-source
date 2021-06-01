import simulation as sim
from geneticAlgorithm.encoding import *
from geneticAlgorithm.utils import *
from geneticAlgorithm.fitnessFunctions import coherentFitness

def runExperiment(encodedTrap, numSimulations= 10000, intention=False, printStatistics = True):
    """
    Takes in a trap and runs `numSimulations` simulations at 5 different hunger levels.
    Tallies the number of alive gophers and returns the proportion of alive gophers as well as the
    standard error.
    """
    decodedTrap = singleDecoding(encodedTrap)

    numberAlive = 0
    hungerLevels = 5
    for _ in range(int(numSimulations)):    
        for hunger in range(hungerLevels):
            numberAlive += int(sim.simulateTrap(createTrap(decodedTrap), intention, hunger = hunger / 5)[3])

    # Calculate statistics
    proportion = numberAlive / (numSimulations * hungerLevels)
    stderr = np.sqrt(proportion * (1 - proportion) / (numSimulations * hungerLevels))

    if printStatistics:
        upperCI = proportion + 1.96 * stderr
        lowerCI = proportion - 1.96 * stderr

        print("Proportion: ", proportion)
        print("Std Error: ", round(stderr, 3))
        print("CI: [", round(lowerCI, 3), ", ", round(upperCI, 3), "]")

    return proportion, stderr

# runExperiment([18, 56, 14, 29, 1, 17, 49, 2, 17, 44, 0, 24], intention=True)
