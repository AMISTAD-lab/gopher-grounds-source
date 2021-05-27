import cellarray as ca
import numpy as np
import itertools
from classes.Door import *
from classes.Floor import *
from classes.Food import *
from classes.Dirt import *
from classes.Wire import *
from classes.Arrow import *
from classes.Cell import *
from designedTraps import *

## IMPORTANT: For every encoded trap, the following must be true to be a valid config:
    ## trap[4] = 2
    ## trap[7] = 0
    ## trap[10] = 1

def singleEncoding(trap):
    """
    Takes a trap and returns a 1x12 numpy int array encoding it
    Each sequence of three items in the array represents a row of the trap grid
    """
    encoded = []
    flatten_trap = list(itertools.chain(*trap))
    for cell in flatten_trap:
        encoded.append(ca.find_index(cell))
    return np.array(encoded)

def listEncoding(traps):
    """Given a list of n non-encoded traps, return a nx12 numpy array with the encoded versions of the traps"""
    # encode traps
    encodedTraps = []
    for trap in traps:
        encodedTraps.append(singleEncoding(trap))
    return np.array(encodedTraps)

def checkDifferences(traps):
    """Given a list of non-encoded traps, determine if there are differences between the columns
    across all encoded traps in the list. Returns numpy array with 'diff' in any column with at least one difference,
    otherwise puts the shared value in that position."""
    result = []
    traps = listEncoding(traps)
    for i in range(12):
        different = False
        firstVal = traps[0][i]
        for j in range(len(traps)):
            if firstVal != traps[j][i]:
                different = True
                break
            else:
                continue
        if different:
            result.append('diff')
        else:
            result.append(firstVal)
    return result

def singleDecoding():
    """Takes an encoded trap and decodes it back into normal form"""
    pass

def listDecoding():
    """Takes an list of encoded traps and decodes its elements back into normal form"""
    pass