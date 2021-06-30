import numpy as np
import os
import webbrowser
import classes.Trap as TrapClass
import geneticAlgorithm.encoding as encoding
from geneticAlgorithm.main import geneticAlgorithm
import libs.simulation as sim
import libs.visualize as vis

def createTrap(configuration):
    """Takes in a board configuration and wraps that configuration in a trap class"""
    return TrapClass.Trap(len(configuration[0]), len(configuration), False, chosenBoard = configuration)

def convertStringToEncoding(strEncoding, delim=','):
    """Takes in an encoding as a string and returns that encoding as a list"""
    strList = strEncoding.strip()[1:-1] # getting the numbers
    digitList = strList.split(delim) # splitting number strings by digits
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

def simulateTrapInBrowser(listEncoding, hunger=0, intention=False, noAnimation=False, gopherState=[1, 4, 0, 1], frame = 0):
    """Takes in a list encoding and simulates the trap in the browser"""
    decodedList = encoding.singleDecoding(listEncoding)
    simulationInfo = sim.simulateTrap(createTrap(decodedList), intention, hunger=hunger, forceEnter=True)[:3]
    vis.writeTojs([simulationInfo], noAnimation, gopherState, frame)

    # opens the animation in the web browser
    webbrowser.open_new_tab("file://" + os.path.realpath("./animation/animation.html"))
