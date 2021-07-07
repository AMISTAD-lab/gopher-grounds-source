import numpy as np
import pandas as pd
from typing import List, Union
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

    frequency = cursor.execute(f' \
        SELECT SUM([frequency]) FROM {FREQ_TABLE} \
        WHERE [function] = :function AND [trap] = :trap;',
        { 'function': function, 'trap': trap }
    ).fetchone()

    if not frequency:
        return 0

    # Closing cursor
    cursor.close()

    return frequency[0]

def getSingleLethalityCount(fitness: str) -> pd.DataFrame:
    '''
    Returns a list of pairs (count, lethality), which represents the number of traps with a given lethality.
    The fitness function to filter by must be passed in as well.
    '''
    cursor = client.cursor()

    cursor.execute(f' \
        SELECT [lethality], SUM([frequency]) FROM {FREQ_TABLE} \
        WHERE [function] = :function \
        GROUP BY [lethality];',
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

    # Creating proportions instead of frequencies
    ser = pd.Series(lethPoints, name=fitness)
    if ser.to_numpy().sum():
        ser /= ser.to_numpy().sum()

    return ser

def getSingleCoherenceCount(fitness: str) -> pd.DataFrame:
    '''
    Returns a list of pairs (count, coherence), which represents the number of traps with a given lethality.
    The fitness function to filter by must be passed in as well.
    '''
    cursor = client.cursor()

    cursor.execute(f' \
        SELECT [coherence], SUM([frequency]) FROM {FREQ_TABLE} \
        WHERE [function] = :function \
        GROUP BY [coherence];',
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

    # Creating proportions instead of frequencies
    ser = pd.Series(cohPoints, name=fitness)
    if ser.to_numpy().sum():
        ser /= ser.to_numpy().sum()

    return ser

def getTotalLethalityCounts() -> pd.DataFrame:
    '''
    Returns a data frame where the columns correspond to different fitness functions, and each cell 
    represents the number of traps with a given lethality.
    '''
    # Create a list of series for each of the coherence counts per function
    serList = [getSingleLethalityCount(func) for func in (*constants.FUNCTIONS, 'designed')]
    
    df = pd.concat(serList, axis=1)
    df.fillna(0, inplace=True)
    
    df.rename(
        index={ ind: '%.3f' % ind for ind in df.index },
        columns={
            'multiobjective': 'multiobj',
            'binary-distance': 'hamming',
        },
        inplace=True
    )

    return df

def getTotalCoherenceCounts() -> pd.DataFrame:
    '''
    Returns a data frame where the columns correspond to different fitness functions, and each cell 
    represents the number of traps with a given lethality.
    '''
    # Create a list of series for each of the coherence counts per function
    serList = [getSingleCoherenceCount(func) for func in (*constants.FUNCTIONS, 'designed')]
    
    df = pd.concat(serList, axis=1)
    df.fillna(0, inplace=True)
    
    df.rename(
        index={ ind: '%.3f' % ind for ind in df.index },
        columns={
            'multiobjective': 'multiobj',
            'binary-distance': 'hamming',
        },
        inplace=True
    )

    return df

def getLethalityData(fitness: str) -> pd.DataFrame:
    '''
    Returns a pandas DataFrame of dictionaries of lethality -> coherence[], where each key is a lethality
    value, and each value is a list of all the counts of the respective coherence value (by index) as
    defined in the geneticAlgorithm.constants file.
    '''
    cursor = client.cursor()

    cursor.execute(f' \
        SELECT SUM([frequency]), [lethality], [coherence] FROM {FREQ_TABLE} \
        WHERE [function] = :function \
        GROUP BY [lethality], [coherence];',
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

    df = pd.DataFrame(lethPoints)

    # Rename dataframe to have column/index names w/ standardized number of digits
    df.rename(columns={ leth: '%.3f' % leth for leth in constants.lethalities }, inplace=True)
    df.rename(index={ coher: '%.3f' % coher for coher in constants.coherences }, inplace=True)

    ## Get proportions
    if df.to_numpy().sum():
        df /= df.to_numpy().sum()

    return df

def getCoherenceData(fitness: str) -> pd.DataFrame:
    '''
    Returns a list of dictionaries of threshold -> List pairs, where each value contains a list
    of all the data points whose coherence values are contained in the given interval [low, high].
    The list is split into two dictionaries [intention, noIntention]
    '''
    cursor = client.cursor()

    cursor.execute(f' \
        SELECT SUM([frequency]), [coherence], [lethality] FROM {FREQ_TABLE} \
        WHERE [function] = :function \
        GROUP BY [coherence], [lethality];',
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

    df = pd.DataFrame(cohPoints)

    # Rename dataframe to have column/index names w/ standardized number of digits
    df.rename(columns={ coher: '%.3f' % coher for coher in constants.coherences }, inplace=True)
    df.rename(index={ leth: '%.3f' % leth for leth in constants.lethalities }, inplace=True)

    ## Get proportions
    if df.to_numpy().sum():
        df /= df.to_numpy().sum()

    return df

def getGenerationData(func: str) -> np.ndarray:
    '''
    Returns a 3 x n np array of [coherence, lethality, genRange] vals which holds 
    all the coherence and lethality data split into 10 generation ranges (as enumerated
    in constants.generations)
    '''
    cursor = client.cursor()

    cursor.execute(f' \
        SELECT [coherence], [lethality], generation, SUM([frequency]) \
        FROM {FREQ_TABLE} WHERE [function] = :function \
        GROUP BY generation, [coherence], [lethality] \
        ORDER BY generation DESC; \
    ', { 'function': func })

    coherenceArr = []
    lethalitiesArr = []
    genRangeArr = []

    for (coh, leth, genRange, freq) in cursor.fetchall():
        for _ in range(freq):
            coherenceArr.append(coh)
            lethalitiesArr.append(leth)
            genRangeArr.append(genRange)

    return np.array([coherenceArr, lethalitiesArr, genRangeArr])

    # coherence = []
    # lethalities = []
    # generations = []
    # frequencies = []

    # for (coh, leth, gen, freq) in cursor.fetchall():
    #     coherence.append(coh)
    #     lethalities.append(leth)
    #     generations.append(gen)
    #     frequencies.append(freq)

    # return np.array([coherence, lethalities, generations, frequencies])