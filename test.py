import csv
import time
import geneticAlgorithm.constants as constants
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.utils as utils

directory = 'frequencies'
inputFiles = (f'./{directory}/functionalPart{i}.csv' for i in (1, 2, 3))
outputFile = f'./{directory}/functional.csv'
headers = constants.experimentHeaders if directory == 'csv' else constants.frequencyHeaders

def reformatFunctional(file):
    with open(file, 'r') as fRead:
        reader = csv.reader(fRead)
        acc = []
        for i, row in enumerate(reader):
            if i == 0:
                acc.append(constants.frequencyHeaders)
                continue

            acc.append([
                *row[0:5],
                row[4],
                *row[5:],
                round(functions.combinedFitness(utils.convertStringToEncoding(row[2], delim=' ')), 4)
            ])

    with open(file, 'w+') as fWrite:
        writer = csv.writer(fWrite)
        writer.writerows(acc)

def reset():
    with open(f'./{directory}/functionalPart1.csv', 'r') as fRead, open('./test.csv', 'w+') as fWrite:
        reader = csv.reader(fRead)
        writer = csv.writer(fWrite)
        acc = []
        for i, row in enumerate(reader):
            writer.writerow(row)

            # [
            #     *row[0:5],
            #     row[4],
            #     *row[5:],
            #     round(functions.combinedFitness(utils.convertStringToEncoding(row[2], delim=' ')), 4)
            # ]

            if i > 100:
                break
        

def createExperimentCSV(inputFiles, outputFile, headers):
    with open(outputFile, 'w+') as out:
        writer = csv.writer(out)
        writer.writerow(headers)

    with open(outputFile, 'a') as fWrite:
        writer = csv.writer(fWrite)
        for inputFile in inputFiles:
            with open(inputFile, 'r') as fRead:
                reader = csv.reader(fRead)

                for row in reader:
                    for i, row in enumerate(reader):
                        if i == 0:
                            continue

                        writer.writerow([
                            *row[:4],
                            int(row[4] == 'True'),
                            *row[5:7],
                            round(functions.combinedFitness(utils.convertStringToEncoding(row[1])), 4),
                            *row[7:],
                        ])


reset()
start = time.time()
reformatFunctional('./test.csv')
print(round(time.time() - start, 4))