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

def encoding(trap):
    """
    Takes a trap and returns a 1x12 numpy int array encoding it
    Each sequence of three items in the array represents a row of the trap grid
    """
    encoded = []
    flatten_trap = list(itertools.chain(*trap))
    for cell in flatten_trap:
        encoded.append(ca.find_index(cell))
    return np.array(encoded)
