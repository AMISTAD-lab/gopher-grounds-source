import libs.algorithms as algo
import goodTuring as gt
from classes.Encoding import Encoding
import geneticAlgorithm.utils as utils
import geneticAlgorithm.constants as constants
import csv

def newIsTrap(encodedTrap, trap, fitnessFunc, sigVal=13.29):
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the real distribution"""
    p = gt.getSmoothedProb(encodedTrap, fitnessFunc)
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

def differenceExperiment(fitnessFunc, encoder: Encoding = None):
    if not encoder:
        encoder = Encoding()

    inputPath = constants.experimentPath.format(enc='old_encoding', func=fitnessFunc, suff='')
    outputPath = constants.experimentPath.format(enc='old_encoding', func=fitnessFunc, suff='SCexperiment')
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
                    encodedTrap = utils.convertStringToEncoding(row[1])
                    decodedTrap = encoder.decode(encodedTrap)
                    trap = utils.createTrap(decodedTrap)
                    old_is_trap = algo.isTrap(trap)
                    new_is_trap = newIsTrap(encodedTrap, trap, fitnessFunc)
                    if old_is_trap != new_is_trap:
                        countDiff += 1
                    writer.writerow(row+[old_is_trap, new_is_trap])
            outcsv.close()
    
    print("{} Proprotion Different: {}".format(fitnessFunc, countDiff / (countTotal/2)))

def freqDifferenceExperiment(fitnessFunc, encoder: Encoding = None):
    if not encoder:
        encoder = Encoding()

    inputPath = constants.frequencyPath.format(enc='old_encoding', func=fitnessFunc, suff='')
    outputPath = constants.frequencyPath.format(enc='old_encoding', func=fitnessFunc, suff='SCexperiment')
    countTotal = 0
    countDiff = 0
    trialNum = 0

    with open(inputPath, 'r', newline='') as incsv:
        with open(outputPath, 'w', newline='') as outcsv:
            writer = csv.writer(outcsv)

            for row in csv.reader(incsv):
                if row[0] == "Trial":
                    writer.writerow(row + ["Old_Is_Trap?", "New_Is_Trap?"])
                else:
                    countTotal += 1
                    if row[0] != trialNum:
                        trialNum = row[0]
                        print(trialNum)
                    encodedTrap = utils.convertStringToEncoding(row[2])
                    decodedTrap = encoder.decode(encodedTrap)
                    trap = utils.createTrap(decodedTrap)
                    old_is_trap = algo.isTrap(trap)
                    new_is_trap = newIsTrap(encodedTrap, trap, fitnessFunc)
                    if old_is_trap != new_is_trap:
                        countDiff += 1
                    writer.writerow(row+[old_is_trap, new_is_trap])
            outcsv.close()
    
    print("{} Proprotion Different: {}".format(fitnessFunc, countDiff / (countTotal)))

# freqDifferenceExperiment("multiobjective")
# freqDifferenceExperiment("functional")
# freqDifferenceExperiment("binary-distance")
# freqDifferenceExperiment("random")


# differenceExperiment("random")
# differenceExperiment("coherence")
# differenceExperiment("functional")
# differenceExperiment("multiobjective")
# differenceExperiment("binary-distance")
