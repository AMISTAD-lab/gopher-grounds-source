import numpy as np
import pandas as pd
from typing import Callable, List, Union
from database.client import client
from database.constants import *
import geneticAlgorithm.constants as constants

def getTrapFreq(trap: Union[str, List[int], np.ndarray], function: str = None) -> int:
    ''' Takes in a trap and returns the frequency of that trap with the fitness function '''
    # Open a cursor
    cursor = client.cursor()

    if not function:
        raise Exception('Need to provide a fitness function to search by')
    
    # Standardizing input type
    if not isinstance(trap, str):
        if isinstance(trap, List):
            trap = np.array(trap)
        
        trap = np.array2string(trap)

    frequency = cursor.execute(' \
        SELECT SUM(frequency) FROM frequencies \
        WHERE function = :function AND trap = :trap; \
        '.format(FREQ_TABLE),
        { 'function': function, 'trap': trap }
    ).fetchone()

    if not frequency:
        return 0

    # Closing cursor
    cursor.close()

    return frequency[0]

def getLethalityCount(fitness: str, limit = 0):
    '''
    Returns a list of pairs (count, lethality), which represents the number of traps with a given lethality.
    The fitness function to filter by must be passed in as well.
    '''
    cursor = client.cursor()

    cursor.execute(' \
        SELECT lethality, SUM(frequency) FROM {} \
        WHERE function = :function \
        GROUP BY lethality;'.format(FREQ_TABLE, f' LIMIT {limit}' if limit else ''),
        { 'function': fitness }
    )

    lethPoints = {}
    for (lethality, count) in cursor.fetchall():
        lethPoints[lethality] = count
    
    # Filling the remaining spots in case they were not present
    for lethality in constants.lethalities:
        if lethality not in lethPoints:
            lethPoints[lethality] = 0

    cursor.close()

    return pd.DataFrame.from_dict(lethPoints, orient='index', columns=['Frequency']).rename_axis('Lethality')

def getCoherenceCount(fitness: str, limit = 0) -> List[dict]:
    '''
    Returns a list of pairs (count, coherence), which represents the number of traps with a given lethality.
    The fitness function to filter by must be passed in as well.
    '''
    cursor = client.cursor()

    cursor.execute(' \
        SELECT coherence, SUM(frequency) FROM {} \
        WHERE function = :function \
        GROUP BY coherence;'.format(FREQ_TABLE, f' LIMIT {limit}' if limit else ''),
        { 'function': fitness }
    )

    cohPoints = {}
    for (coherence, count) in cursor.fetchall():
        cohPoints[coherence] = count
    
    # Filling the remaining spots in case they were not present
    for coherence in constants.coherences:
        if coherence not in cohPoints:
            cohPoints[coherence] = 0

    cursor.close()

    return pd.DataFrame.from_dict(cohPoints, orient='index', columns=['Frequency']).rename_axis('Coherence')

def getLethalityData(fitness: str) -> pd.DataFrame:
    '''
    Returns a pandas DataFrame of dictionaries of lethality -> coherence[], where each key is a lethality
    value, and each value is a list of all the counts of the respective coherence value (by index) as
    defined in the geneticAlgorithm.constants file.
    '''
    cursor = client.cursor()

    cursor.execute(' \
        SELECT SUM(frequency), lethality, coherence FROM {} \
        WHERE function = :function \
        GROUP BY lethality, coherence;'.format(FREQ_TABLE),
        { 'function': fitness }
    )

    lethPoints = {}
    # Getting data from the database and putting the data in a temporary nested dictionary
    for (frequency, lethality, coherence) in cursor.fetchall():
        if lethality not in lethPoints:
            lethPoints[lethality] = {}
        
        lethPoints[lethality][coherence] = frequency

    # Filling all non-present lethality values with empty dictionaries
    for lethality in constants.lethalities:
        if lethality not in lethPoints:
            lethPoints[lethality] = {}
    
    # Converting each nested dictionary to an array, where each index corresponds to the
    # count for the coherence in constants.coherences
    for lethality in lethPoints:
        for coherence in constants.coherences:
            if coherence not in lethPoints[lethality]:
                lethPoints[lethality][coherence] = 0

    return pd.DataFrame(lethPoints)

def getCoherenceData(fitness: str) -> List[dict]:
    '''
    Returns a list of dictionaries of threshold -> List pairs, where each value contains a list
    of all the data points whose coherence values are contained in the given interval [low, high].
    The list is split into two dictionaries [intention, noIntention]
    '''
    cursor = client.cursor()

    cursor.execute(' \
        SELECT SUM(frequency), coherence, lethality FROM {} \
        WHERE function = :function \
        GROUP BY coherence, lethality;'.format(FREQ_TABLE),
        { 'function': fitness }
    )

    cohPoints = {}
    # Getting data from the database and putting the data in a temporary nested dictionary
    for (frequency, coherence, lethality) in cursor.fetchall():
        if coherence not in cohPoints:
            cohPoints[coherence] = {}
        
        cohPoints[coherence][lethality] = frequency

    # Filling all non-present lethality values with empty dictionaries
    for coherence in constants.coherences:
        if coherence not in cohPoints:
            cohPoints[coherence] = {}
    
    # Converting each nested dictionary to an array, where each index corresponds to the
    # count for the coherence in constants.coherences
    for coherence in cohPoints:
        for lethality in constants.lethalities:
            if lethality not in cohPoints[coherence]:
                cohPoints[coherence][lethality] = 0

    return pd.DataFrame(cohPoints)

def getGenerationData(func: str, filter: str) -> pd.DataFrame:
    '''
    Returns a dataframe of generation data vs filter (either coherence or lethality) data,
    where the coherence/lethality value counts are tabulated per 1000 generations
    '''
    pass