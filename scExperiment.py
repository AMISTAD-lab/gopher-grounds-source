import libs.algorithms as algo
import goodTuring as gt
import geneticAlgorithm.encoding as encode
import geneticAlgorithm.utils as utils
import geneticAlgorithm.constants as constants
import csv
import ast

def newIsTrap(encodedTrap, trap, fitnessFunc, sigVal=13.29):
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the real distribution"""
    p = gt.getSmoothedProb(encodedTrap, fitnessFunc)
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

def differenceExperiment(fitnessFunc):

    inputPath = constants.experimentPath.format(fitnessFunc,'')
    outputPath = constants.experimentPath.format(fitnessFunc,'SCexperiment')
    countTotal = 0
    countDiff = 0

    with open(inputPath, 'r' ,newline='') as incsv:
        with open(outputPath, 'w' ,newline='') as outcsv:
            writer = csv.writer(outcsv)

            for row in csv.reader(incsv):
                if row[0] == "Trial":
                    writer.writerow(row + ["Old_Is_Trap?", "New_Is_Trap?"])
                else:
                    countTotal += 1
                    if countTotal % 2 == 0:
                        continue
                    encodedTrap = ast.literal_eval(row[1])
                    decodedTrap = encode.singleDecoding(encodedTrap)
                    trap = utils.createTrap(decodedTrap)
                    old_is_trap = algo.isTrap(trap)
                    new_is_trap = newIsTrap(encodedTrap, trap, fitnessFunc)
                    if old_is_trap != new_is_trap:
                        countDiff += 1
                    writer.writerow(row+[old_is_trap, new_is_trap])
            outcsv.close()
    
    print("{} Proprotion Different: {}".format(fitnessFunc, countDiff / (countTotal/2)))

# def freqDifferenceExperiment(fitnessFunc):

#     inputPath = constants.frequencyPath.format(fitnessFunc, '')
#     outputPath = constants.frequencyPath.format(fitnessFunc, 'SCexperiment')
#     countTotal = 0
#     countDiff = 0

#     with open(inputPath, 'r') as incsv:
#         with open(outputPath, 'w') as outcsv:
#             writer = csv.writer(outcsv)

#             for row in csv.reader(incsv):
#                 if row[0] == "Trial":
#                     writer.writerow(row + ["Old_Is_Trap?", "New_Is_Trap?"])
#                 else:
#                     countTotal += 1
#                     row2 = row[2][1:-1]
#                     print(row2)
#                     encodedTrap = row2.split()
#                     print(encodedTrap)
#                     decodedTrap = encode.singleDecoding(encodedTrap)
#                     trap = utils.createTrap(decodedTrap)
#                     old_is_trap = algo.isTrap(trap)
#                     new_is_trap = algo.newIsTrap(encodedTrap, trap, fitnessFunc)
#                     if old_is_trap != new_is_trap:
#                         countDiff += 1
#                     writer.writerow(row+[old_is_trap, new_is_trap])
#             outcsv.close()
    
#     print("Finished.")
#     print("{} Proprotion Different: {}".format(fitnessFunc, countDiff / countTotal))

differenceExperiment("random")
differenceExperiment("coherence")
differenceExperiment("functional")
differenceExperiment("multiobjective")
differenceExperiment("binary-distance")