import numpy as np
from typing import Callable, List, Union
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

def getLethalityData(fitness: str, interval = (0, 1), limit = 0):
    '''
    Returns a list of dictionaries of threshold -> dict, where each value contains a list
    of all the data points whose lethality values are contained in the given interval [low, high].
    '''
    cursor = client.cursor()

    cursor.execute(' \
        SELECT threshold, GROUP_CONCAT(lethality) FROM frequencies \
        WHERE fitnessFunc = :function AND :intervalLow <= lethality AND lethality <= :intervalHigh \
        GROUP BY threshold{};'.format(f' LIMIT {limit}' if limit else ''),
        { 'function': fitness, 'intervalLow': interval[0], 'intervalHigh': interval[1] }
    )

    points = {}
    for (thresh, csv) in cursor.fetchall():
        points[thresh] = list(map(lambda num : float(num), csv.split(',')))
    
    return points

def getCoherenceData(fitness: str, interval = (0, 1), limit = 0) -> List[dict]:
    '''
    Returns a list of dictionaries of threshold -> List pairs, where each value contains a list
    of all the data points whose coherence values are contained in the given interval [low, high].
    The list is split into two dictionaries [intention, noIntention]
    '''
    cursor = client.cursor()

    cursor.execute(' \
        SELECT threshold, GROUP_CONCAT(coherence) FROM frequencies \
        WHERE fitnessFunc = :function AND :intervalLow < coherence AND coherence <= :intervalHigh \
        GROUP BY threshold{};'.format(f' LIMIT {limit}' if limit else ''),
        { 'function': fitness, 'intervalLow': interval[0], 'intervalHigh': interval[1] }
    )

    points = {}
    for (thresh, csv) in cursor.fetchall():
        points[thresh] = list(map(lambda num : float(num), csv.split(',')))
    
    return points

def getLethalityCount(fitness: str, interval = (0, 1), limit = 0):
    '''
    Returns a list of dictionaries of threshold -> int pairs, where each value refers to the number of
    data points whose lethality values are contained in the given interval [low, high].
    The list is split into two dictionaries [intention, noIntention]
    '''
    cursor = client.cursor()

    cursor.execute(' \
        SELECT threshold, COUNT(lethality) FROM frequencies \
        WHERE fitnessFunc = :function AND :intervalLow <= lethality AND lethality <= :intervalHigh \
        GROUP BY threshold{};'.format(f' LIMIT {limit}' if limit else ''),
        { 'function': fitness, 'intervalLow': interval[0], 'intervalHigh': interval[1] }
    )

    points = {}
    for (thresh, count) in cursor.fetchall():
        points[thresh] = count
    
    return points

def getCoherenceCount(fitness: str, interval = (0, 1), limit = 0) -> List[dict]:
    '''
    Returns a list of dictionaries of threshold -> int pairs, where each value refers to the number of
    data points whose coherence values are contained in the given interval [low, high].
    The list is split into two dictionaries [intention, noIntention]
    '''
    cursor = client.cursor()

    cursor.execute(' \
        SELECT threshold, COUNT(coherence) FROM frequencies \
        WHERE fitnessFunc = :function AND :intervalLow < coherence AND coherence <= :intervalHigh \
        GROUP BY threshold{};'.format(f' LIMIT {limit}' if limit else ''),
        { 'function': fitness, 'intervalLow': interval[0], 'intervalHigh': interval[1] }
    )

    points = {}
    for (thresh, count) in cursor.fetchall():
        points[thresh] = count
    
    return points

def getHistogram(fitness: str, numBins: int, dataFunc: Callable) -> List[dict]:
    '''
    Returns 2 dictionaries [intentionDict, noIntentionDict]. Each dictionary has threshold -> List
    pairs, where the List is a numBins-length list, containing the count for each bin.
    The dataFunc must be one of getLethalityCount or getCoherenceCount
    '''
    intervals = []
    for i in range(numBins):
        currInterval = [i / numBins, (i + 1) / numBins]
        
        # Make the range exclusive of the upper bound unless we are in the last bin
        if i + 1 < numBins:
            currInterval[1] -= 1e-4
        
        intervals.append(currInterval)
    
    retDict = [{}, {}]
    for interval in intervals:
        res = dataFunc(fitness, interval)

        for i, dic in enumerate(res):
            for key in (0.2, 0.4, 0.6, 0.8, 1.0):
                if key not in retDict[i]:
                    retDict[i][key] = []

                retDict[i][key].append(dic[key] if key in dic else 0)

    return retDict