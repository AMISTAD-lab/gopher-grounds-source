'''
this file is a script that generates uniform random data. it writes the data to
./uniform-random/uniform-random_new_enc_{i}.csv, where i is a parameter passed in.
furthermore, it can take in an argument to determine how many generations to produce per file.
'''

import csv
import geneticAlgorithm.library as lib
from classes.Encoding import Encoding
import geneticAlgorithm.fitnessFunctions as functions
import argparse
import os

parser = argparse.ArgumentParser(description="Commands to run the experiment")
parser.add_argument('file_num', help='the file number to append to the end of the file', type=int)
parser.add_argument('--generations', '-g', help='the number of generations to run per trial', type=int, default=2000200)
parser.add_argument('--offset', '-o', help='the offset for the file number', type=int, default=0)
args = parser.parse_args()

encoder = Encoding(code=1)
with open(f'./uniform-random/uniform-random_new_enc_{args.file_num + args.offset}.csv', 'w+', newline='') as out:
    writer = csv.writer(out)

    writer.writerow(['Trial', 'Generation', 'Trap', 'Function', 'Fitness', 'Lethality', 'Coherence', 'Combined'])

    for i in range(args.generations):
        trap = lib.generateTrap(encoder)
        writer.writerow([
            -1, -1, trap, 'uniform-random', 0,
            round(functions.getLethality(trap, encoder), 3),
            round(functions.getCoherence(trap, encoder), 3),
            round(functions.getCombined(trap, encoder), 3)
        ])

