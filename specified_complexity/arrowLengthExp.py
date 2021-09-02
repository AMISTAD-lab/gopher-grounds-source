from classes.Encoding import Encoding
import geneticAlgorithm.constants as constants
import geneticAlgorithm.analytical as analytical
import csv
import numpy as np
import geneticAlgorithm.utils as utils

def arrowLengthExp(fitnessFunc, numFiles, enc='new_encoding'):
    if enc == 'new_encoding':
        encoder = Encoding(np.array([9, 6, 3, 0, 1, 2, 5, 8, 11, 10, 7, 4]))
    else:
        encoder = Encoding()

    inputPaths = [constants.experimentPath.format(enc=enc, func=fitnessFunc, suff=f'_new_enc_{index}') for index in range(1,numFiles + 1)]
    outputPath = constants.experimentPath.format(enc=enc, func=fitnessFunc, suff='ArrowLengthExp')
    count = 0
    sumLength = 0 
    
    header = ["Trial", "Trap", "leftLength", "rightLength", "totalLength"]
    with open(outputPath, 'w' ,newline='') as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(header)
        for inputPath in inputPaths:
            with open(inputPath, 'r' ,newline='') as incsv:
                    for row in csv.reader(incsv):
                        if row[0] == "Trial":
                            continue
                        else:
                            count += 1
                            if count % 2 == 0:
                                continue
                            encodedTrap = utils.convertStringToEncoding(row[1])
                            decodedTrap = encoder.decode(encodedTrap)
                            leftLength, rightLength, totalLength = analytical.getArrowLength(decodedTrap)
                            sumLength += totalLength
                            writer.writerow([int(count / 2), row[1], leftLength, rightLength, totalLength])
    outcsv.close()
    
    print("{} Average total length: {}".format(fitnessFunc, sumLength / (count/2)))