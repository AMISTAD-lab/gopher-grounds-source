from numpy.core.fromnumeric import reshape
import cellarray as ca
import numpy as np
from classes.Door import *
from classes.Floor import *
from classes.Food import *
from classes.Dirt import *
from classes.Wire import *
from classes.Arrow import *
from classes.Cell import *
from designedTraps import *
import copy

## IMPORTANT: For every encoded trap, the following must be true to be a valid config:
    ## trap[4] = 2  # Food
    ## trap[7] = 0  # Floor
    ## trap[10] = 1 # Door

def singleEncoding(board):
    """
    Takes a board (4 x 3 array of cells) and returns a 1x12 numpy int array encoding it
    Each sequence of three items in the array represents a row of the trap grid
    """
    flatten_trap = np.ndarray.flatten(np.array(board))
    return np.array([ca.findIndex(cell) for cell in flatten_trap])

def singleEncoding1(board):
    """
    With fitness version: Takes a board with fitness value (5 x 3 array of cells) and returns a 1 x 15 numpy int array encoding it
    Each sequence of three items in the array represents a row of the trap grid
    """
    flatten_trap = np.ndarray.flatten(np.array(board))
    result = []
    for i in range(12):
        result.append(ca.findIndex(flatten_trap[i]))  
    for i in range(12,15):
        result.append(flatten_trap[i])  
    return np.array(result)

def listEncoding(traps):
    """Given a list of n non-encoded traps, return a nx12 numpy array with the encoded versions of the traps"""
    # encode traps
    encodedTraps = []
    for trap in traps:
        encodedTraps.append(singleEncoding(trap))
    return np.array(encodedTraps)

def listEncoding1(traps):
    """With fitness version: Given a list of n non-encoded traps, return a nx15 numpy array with the encoded versions of the traps"""
    # encode traps
    encodedTraps = []
    for trap in traps:
        encodedTraps.append(singleEncoding1(trap))
    return np.array(encodedTraps)

## TODO: Come back and make this more readable
def checkDifferences(traps):
    """Given a list of non-encoded traps, determine if there are differences between the columns
    across all encoded traps in the list. Returns numpy array with -1 in any column with at least one difference,
    otherwise puts the shared value in that position.
    Note: This function is for testing purposes
    """
    result = []
    traps = listEncoding(traps)
    for i in range(12):
        different = False
        firstVal = traps[0][i]
        for j in range(1, len(traps)):
            if firstVal != traps[j][i]:
                different = True
                break
        if different:
            result.append(-1)
        else:
            result.append(firstVal)
    return result

def singleDecoding(encodedTrap):
    """Takes an encoded trap (1 x 12 array) and decodes it back into normal form"""
    encodedTrap = np.array(encodedTrap).reshape((4, 3))
    decodedTrap = []
    for y in range(len(encodedTrap)):
        row = []
        for x in range(len(encodedTrap[0])):
            cell = copy.deepcopy(ca.cells[int(encodedTrap[y][x])])
            cell.x = x
            cell.y = y

            row.append(cell)

        decodedTrap.append(row)
    return np.array(decodedTrap)

def singleDecoding1(encodedTrap):
    """With fitness version: Takes an encoded trap (1 x 15 array) and decodes it back into normal form"""
    encodedTrap = np.array(encodedTrap).reshape((5, 3))
    decodedTrap = []
    for y in range(len(encodedTrap)-1):
        row = []
        for x in range(len(encodedTrap[0])):
            cell = copy.deepcopy(ca.cells[int(encodedTrap[y][x])])
            cell.x = x
            cell.y = y

            row.append(cell)

        decodedTrap.append(row)
    decodedTrap.append(encodedTrap[4])
    return np.array(decodedTrap)

def listDecoding(encodedTrapList):
    """Takes an list of encoded traps and decodes its elements back into normal form - returns an n x 4 x 3 list"""
    return np.array([singleDecoding(encodedTrap) for encodedTrap in encodedTrapList])

def listDecoding1(encodedTrapList):
    """Takes an list of encoded traps and decodes its elements back into normal form - returns an n x 5 x 3 list"""
    return np.array([singleDecoding1(encodedTrap) for encodedTrap in encodedTrapList])

