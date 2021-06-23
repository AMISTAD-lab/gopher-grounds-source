import libs.algorithms as algo
import goodTuring as gt
import geneticAlgorithm.encoding as encode
import geneticAlgorithm.utils as utils
import csv
import ast

def differenceExperiment(fitnessFunc):
    fofDict = gt.loadFoF(fitnessFunc)
    sgtDict = gt.sgtProbs(fofDict)

    inputPath = './csv/{}/{}ExperimentData.csv'.format(fitnessFunc, fitnessFunc)
    outputPath = './csv/{}/{}ExperimentSC.csv'.format(fitnessFunc, fitnessFunc)
    countDiff = 0

    with open(inputPath, 'r') as incsv:
        with open(outputPath, 'w') as outcsv:
            writer = csv.writer(outcsv)

            for row in csv.reader(incsv):
                if row[0] == "Experiment ":
                    writer.writerow(row + ["Old_Is_Trap?", "New_Is_Trap?"])
                else:
                    encodedTrap = ast.literal_eval(row[1])
                    decodedTrap = encode.singleDecoding(encodedTrap)
                    trap = utils.createTrap(decodedTrap)
                    old_is_trap = algo.isTrap(trap)
                    new_is_trap = algo.newIsTrap(encodedTrap, trap, fitnessFunc, sgtDict)
                    if old_is_trap != new_is_trap:
                        countDiff += 1
                    writer.writerow(row+[old_is_trap, new_is_trap])
            outcsv.close()
    
    print("Finished.")
    print(countDiff)

differenceExperiment("random")