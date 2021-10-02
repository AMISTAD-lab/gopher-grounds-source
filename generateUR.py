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
parser.add_argument('file_num', help='the file number to append to the end of the file')
parser.add_argument('generations', help='the number of generations to run per trial', type=int, default=200200)
args = parser.parse_args()

if not os.path.exists('./uniform-random'):
    os.mkdir('./uniform-random')

write_data = [['Trial', 'Generation', 'Trap', 'Function', 'Fitness', 'Lethality', 'Coherence', 'Combined']]
encoder = Encoding(code=1)

for i in range(args.generations):
    trap = lib.generateTrap(encoder)
    write_data.append([
        -1, -1, trap, 'uniform-random', 0,
        round(functions.getLethality(trap, encoder), 3),
        round(functions.getCoherence(trap, encoder), 3),
        round(functions.getCombined(trap, encoder), 3)
    ])

with open(f'./uniform-random/uniform-random_new_enc_{args.file_num}.csv', 'w+', newline='') as out:
    csv.writer(out).writerows(write_data)
