import numpy as np
import classes.Trap as TrapClass
import geneticAlgorithm.encoding as encoding

def createTrap(configuration):
    """Takes in a board configuration and wraps that configuration in a trap class"""
    return TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration)

def convertStringToEncoding(strEncoding, delimiter=','):
    """Takes in an encoding as a string and returns that encoding as a list"""
    if delimiter not in strEncoding:
        delimiter = ' '

    strList = strEncoding.strip()[1:-1] # getting the numbers
    digitList = strList.split(delimiter) # splitting number strings by digits

    return np.array([int(digit.strip()) for digit in digitList if digit])

def convertEncodingToString(encoding):
    """Takes in an encoding and returns the string version of it"""
    encodingStr = '[ '

    for i, elem in enumerate(encoding):            
        encodingStr += '{}'.format(str(elem))
        if i < len(encoding) - 1:
            encodingStr += ', '
    encodingStr += ' ]'
    
    return encodingStr

def convertStringToDecoding(strEncoding):
    """ Takes in a string encoding and returns the decoded trap """
    return encoding.singleDecoding(convertStringToEncoding(strEncoding))

