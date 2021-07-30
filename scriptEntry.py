import argparse
import csv
import os
from classes.Encoding import Encoding
from geneticAlgorithm.library import generateTrap
import geneticAlgorithm.fitnessFunctions as functions

def generateUniformRandomTraps(index):
    encoder = Encoding(code=1)
    write_data = [['Trial', 'Generation', 'Trap', 'Function', 'Fitness', 'Lethality', 'Coherence', 'Combined']]

    for _ in range(8000080):
        trap = generateTrap(encoder)
        lethality = round(functions.getLethality(trap, encoder), 4)
        coherence = round(functions.getCoherence(trap, encoder), 4)
        combined = round(functions.getCombined(trap, encoder), 4)

        write_data.append([-1, -1, trap, 'uniform-random', 0, lethality, coherence, combined])


    if not os.path.exists('./uniform-random/'):
        os.mkdir('./uniform-random/')
    
    with open(f'./uniform-random/uniform_random_new_enc_{index}.csv', 'w+', newline='') as out:
        csv.writer(out).writerows(write_data)


parser = argparse.ArgumentParser(description="")
parser.add_argument('index', type=int, default=1)

args = parser.parse_args()

generateUniformRandomTraps(args.index)
