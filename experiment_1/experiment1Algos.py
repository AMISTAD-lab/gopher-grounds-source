import libs.algorithms as algo
import experiment_1.goodTuring as gt
from classes.Encoding import Encoding
import geneticAlgorithm.utils as utils
import geneticAlgorithm.constants as constants
import csv

#Defining pieces necessary for fsc
TOTAL = 427929800129788411
p = 1 / TOTAL

def isTrap_uniform_high(encodedTrap, trap, fitnessFunc, sigVal=13.29):
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the unifrom distribution and low significant value"""
    global p
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

def isTrap_uniform_low(encodedTrap, trap, fitnessFunc, sigVal=6.645): # Need to fix this value according to alpha value!
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the unifrom distribution and low significant value"""
    global p
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

def isTrap_real_high(encodedTrap, trap, fitnessFunc, sigVal=13.29):
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the real distribution"""
    global p
    if fitnessFunc != "designed":
        p = gt.getSmoothedProb(encodedTrap, fitnessFunc)
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

def isTrap_real_low(encodedTrap, trap, fitnessFunc, sigVal=6.645): # Need to fix this value according to alpha value!
    """given a trap and a significant value, determines whether the trap is coherent enough to be considered designed based on the real distribution"""
    global p
    if fitnessFunc != "designed":
        p = gt.getSmoothedProb(encodedTrap, fitnessFunc)
    connectionTuple = algo.connectionsPerPiece(trap)
    return algo.functional_specified_complexity(connectionTuple, p) >= sigVal

   

def scExperiment(fitnessFunc, num_files, encoder: Encoding = None):
    if not encoder:
        encoder = Encoding(code = 1)

    countTotal = 0

    for i in range(num_files):
        if fitnessFunc == "designed":
            inputPath = constants.getExperimentPath(func=fitnessFunc, suff='')
            outputPath = constants.getExperimentResultPath(number=1, func=fitnessFunc, suff='_scResults')
        else:
            input_suff = "_new_enc_{}".format(i + 1)
            output_suff = "scResults_{}".format(i + 1)
            inputPath = constants.getExperimentPath(func=fitnessFunc, suff=input_suff)
            outputPath = constants.getExperimentResultPath(number=1, func=fitnessFunc, suff=output_suff)

        with open(inputPath, 'r' ,newline='') as incsv:
            with open(outputPath, 'w' ,newline='') as outcsv:
                writer = csv.writer(outcsv)

                for row in csv.reader(incsv):
                    if row[0] == "Experiment":
                        writer.writerow(row + ["isTrap_uniform_high", "isTrap_uniform_low", "isTrap_real_high", "isTrap_real_low"])
                    else:
                        countTotal += 1
                        if countTotal % 2 == 0:
                            continue
                        encodedTrap = utils.convertStringToEncoding(row[2])
                        decodedTrap = encoder.decode(encodedTrap)
                        trap = utils.createTrap(decodedTrap)
                        isTrap_uniform_high_results = isTrap_uniform_high(encodedTrap, trap, fitnessFunc)
                        isTrap_uniform_low_results = isTrap_uniform_low(encodedTrap, trap, fitnessFunc)
                        isTrap_real_high_results = isTrap_real_high(encodedTrap, trap, fitnessFunc)
                        isTrap_real_low_results = isTrap_real_low(encodedTrap, trap, fitnessFunc)
                        writer.writerow(row+[ isTrap_uniform_high_results, isTrap_uniform_low_results, isTrap_real_high_results, isTrap_real_low_results])
                outcsv.close()
    
    print("test total count:", countTotal)