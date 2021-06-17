import numpy as np
from typing import List, Union
from database.client import client
from database.constants import *

def getTrapFreq(trap: Union[str, List[int], np.ndarray], fitnessFunc: str = None) -> Union[List, int]:
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

    frequency = cursor.execute(
        'SELECT frequency, fitnessFunc FROM {} \
        WHERE fitnessFunc = :function AND trap = :trap \
        GROUP BY fitnessFunc;'.format(FREQ_TABLE),
        queryData
    ).fetchone()

    if not frequency:
        return 0

    # Closing cursor
    cursor.close()

    return frequency

def addFreq(trap: Union[str, List[int], np.ndarray], function: str):
    ''' Increments the frequency of the given trap in the database '''
    # Standardizing input type
    if not isinstance(trap, str):
        if isinstance(trap, List):
            trap = np.array(trap)
    
    cursor = client.cursor()

    # Add the frequency to the database if it is not there, then increment its frequency
    cursor.execute(
        'INSERT OR IGNORE INTO {} VALUES (?, ?, ?);'.format(FREQ_TABLE),
        [trap, 0, function]
    )
    cursor.execute(
        'UPDATE {} SET frequency = frequency + 1 WHERE trap = ? AND fitnessFunc = ?;'.format(FREQ_TABLE),
        [trap, function]
    )

    # Commit the changes and close the cursor
    client.commit()
    cursor.close()

def addFreqs(trap: dict, function: str):
    '''
    Increments each trap in the dictionary by its value.
    The keys of the dictionary are the string encodings of the trap.
    '''
    cursor = client.cursor()

    insertCommand = [[key, 0, function] for key in trap]
    updateCommand = [[trap[key], key, function] for key in trap]

    # Add the frequency to the database if it is not there, then increment its frequency
    cursor.executemany(
        'INSERT OR IGNORE INTO {} VALUES (?, ?, ?);'.format(FREQ_TABLE),
        insertCommand
    )
    cursor.executemany(
        'UPDATE {} SET frequency = frequency + ? WHERE trap = ? AND fitnessFunc = ?;'.format(FREQ_TABLE),
        updateCommand
    )

    # Commit the changes and close the cursor
    client.commit()
    cursor.close()
