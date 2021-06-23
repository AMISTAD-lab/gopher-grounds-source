import numpy as np
from typing import List, Union
from database.client import client
from database.constants import *

def getTrapFreq(trap: Union[str, List[int], np.ndarray], fitnessFunc: str = None) -> int:
    ''' Takes in a trap and returns the frequency of that trap with the fitness function '''
    # Open a cursor
    cursor = client.cursor()

    if not fitnessFunc:
        raise Exception('Need to provide a fitness function to search by')
    
    # Standardizing input type
    if not isinstance(trap, str):
        if isinstance(trap, List):
            trap = np.array(trap)
        
        trap = np.array2string(trap)
    
    queryData = {
        'function': fitnessFunc,
        'trap': trap
    }

    frequency = cursor.execute('\
        SELECT SUM(frequency) FROM frequencies \
        WHERE fitnessFunc = :function AND trap = :trap; \
        '.format(FREQ_TABLE),
        queryData
    ).fetchone()

    if not frequency:
        return 0

    # Closing cursor
    cursor.close()

    return frequency[0]

def createFoF(fitness: str):
    # Open a cursor
    cursor = client.cursor()

    if not fitness:
        raise Exception('Need to provide a fitness function to search by')

    cursor.execute(' \
        SELECT totalFreq, COUNT(totalFreq) FROM ( \
            SELECT SUM(frequency) as totalFreq FROM frequencies \
            WHERE fitnessFunc = :fitness \
            GROUP BY trap \
        ) \
        GROUP BY totalFreq; \
    ', { 'fitness': fitness })

    freqOfFreqs = {}

    for [freq, fof] in cursor.fetchall():
        freqOfFreqs[freq] = fof

    cursor.close()

    return freqOfFreqs
