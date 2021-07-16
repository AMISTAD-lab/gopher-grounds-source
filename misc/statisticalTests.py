import numpy as np
import pandas as pd
import random
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.experiment as exp
import geneticAlgorithm.encoding as enc

lethalityDict = {}

def generateRandomTraps(numTraps=100000):
    """Generates numTraps traps uniformly at random. Returns list of decoded traps."""
    traps = []
    for _ in range(numTraps):
        trap = []
        for i in range(12):
            if i == 4:
                trap.append(1)
            elif i == 7:
                trap.append(2)
            elif i == 10:
                trap.append(0)
            else:
                trap.append(random.randrange(2,93,1))
        traps.append(trap)
    return enc.listDecoding(traps)
            
def getStats(traps):
    """Given a list of encoded traps, returns a pandas df with each coherence and lethality"""
    coherences = []
    lethalities = []
    for trap in traps:
        coherences.append(functions.getCoherence(trap))
        lethality, _, _ = exp.runSimulations(enc.singleEncoding(trap), numSimulations=1000, printStatistics = False)
        lethalities.append(lethality)
    stats = {'Coherence': coherences, 'Lethality': lethalities}
    df = pd.DataFrame(stats, columns = ['Coherence', 'Lethality'])
    return df

stats = getStats(generateRandomTraps())
