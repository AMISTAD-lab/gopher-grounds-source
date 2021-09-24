import copy
from typing import List
import numpy as np
import geneticAlgorithm.cellarray as ca

## IMPORTANT: For every encoded trap, the following must be true to be a valid config:
## trap[4] = 2  # Food
## trap[7] = 0  # Floor
## trap[10] = 1 # Door

class Encoding():
    def __init__(self, permutation: List[int] = None, code = 0):
        if permutation is None and code == 0:
            self._permutation = np.array([x for x in range(12)])
            self._code = code
        elif code == 1 or np.allclose(permutation, [9, 6, 3, 0, 1, 2, 5, 8, 11, 10, 7, 4]):
            self._permutation = np.array([9, 6, 3, 0, 1, 2, 5, 8, 11, 10, 7, 4])
            self._code = 1
        else:
            self._permutation = np.array(permutation)
            self._code = -1 
        
        self.door = np.where(self._permutation == 10)[0][0]
        self.floor = np.where(self._permutation == 7)[0][0]
        self.food = np.where(self._permutation == 4)[0][0]

    def encode(self, board) -> np.ndarray:
        '''
        Takes a board (4 x 3 array of cells) and returns a 1x12 numpy int array encoding it
        Each sequence of three items in the array represents a row of the trap grid
        '''
        flattened = np.ndarray.flatten(np.array(board))

        return np.array([ca.findIndex(flattened[i]) for i in self._permutation])
    
    def decode(self, encoded) -> np.ndarray:
        '''
        Takes an encoded trap (1 x 12 array) and decodes it back into normal form
        '''
        # Convert to the normal [0..11] encoding
        canonical = 12 * [-1]
        for i in self._permutation:
            canonical[self._permutation[i]] = encoded[i]
        
        canonical = np.reshape(canonical, (4, 3))
        # Decode all elements
        decodedTrap = []
        for y in range(len(canonical)):
            row = []
            for x in range(len(canonical[0])):
                cell = copy.deepcopy(ca.cells[int(canonical[y][x])])
                cell.x = x
                cell.y = y

                row.append(cell)

            decodedTrap.append(row)
        return np.array(decodedTrap)
    
    def from_canonical(self, canonical) -> np.ndarray:
        ''' Takes an encoding in canonical and returns an encoding given by the permutation '''
        encoding = 12 * [0]
        permutation = self.getPermutation()
        for i, num in enumerate(permutation):
            encoding[i] = canonical[num]
        
        return encoding
    
    def to_canonical(self, encoding) -> np.ndarray:
        ''' Takes an encoding in permutation form and returns it in canonical form ([0..11]) '''
        canonical = 12 * [0]
        permutation = self.getPermutation()
        for i, num in enumerate(permutation):
            canonical[num] = encoding[i]
        
        return canonical

    def listEncoding(self, boards) -> np.ndarray:
        ''' Given a list of n non-encoded traps, return a nx12 numpy array with the encoded versions of the traps '''
        encodedTraps = []
        for board in boards:
            encodedTraps.append(self.encode(board))
        return np.array(encodedTraps)

    def listDecoding(self, encoded_boards) -> np.ndarray:
        ''' Takes an list of encoded traps and decodes its elements back into normal form - returns an n x 4 x 3 list '''
        np.array([self.decode(board) for board in encoded_boards])

    def getPermutation(self) -> np.ndarray:
        ''' Returns the permutation of an encoding instance '''
        return np.array(self._permutation)

    def getCode(self) -> int:
        ''' Returns the code of an encoding '''
        return self._code

    def getIndex(self, element):
        ''' Returns an index of the given cell in the permuation '''
        return np.where(self._permutation == element)[0][0]
