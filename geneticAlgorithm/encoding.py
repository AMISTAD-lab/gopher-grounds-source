import copy
import numpy as np
import geneticAlgorithm.cellarray as ca

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

def listEncoding(traps):
    """Given a list of n non-encoded traps, return a nx12 numpy array with the encoded versions of the traps"""
    # encode traps
    encodedTraps = []
    for trap in traps:
        encodedTraps.append(singleEncoding(trap))
    return np.array(encodedTraps)

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

def listDecoding(encodedTrapList):
    """Takes an list of encoded traps and decodes its elements back into normal form - returns an n x 4 x 3 list"""
    return np.array([singleDecoding(encodedTrap) for encodedTrap in encodedTrapList])
