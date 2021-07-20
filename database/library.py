import numpy as np
import pandas as pd
import statistics as stats
from typing import List, Union

from progress.bar import IncrementalBar
from database.client import client
from database.constants import *
import geneticAlgorithm.constants as constants

##############################
##     Helper Functions     ##
##############################
def getAverageFitnesses(genList, fitList, start=0, end=10000, step=1, conf_interval=1.96, debug=False):
    '''
    Takes in a lists of lists of generations and fitnesses, where each index corresponds to the 
    generation that the fitness was found and the new optimal fitness.
    Aggregates the average best fitness for each generation (determined by start, end, step,
    inclusive) and returns an array of generations, average best fitnesses, and standard errors.
    Ex: getAverageFitnesses([[0, 2, 3, 5]], [[1, 3, 5, 7]], 0, 7, 1) = 
        [1, 2, 3, 4, 5, 6, 7], [1, 1, 1.67, 2.5, 3, 3.67, 4.14, ]
    '''
    if debug:
        print('trial, generation, index, genMarker, fitMarker, genList, fitList')

    # Adding lists to keep track of generation fitness changes
    numTrials = len(genList); indexes = numTrials * [0]
    generations = []; avgFitnesses = []; variances = []
    totalSum = 0
    for generation in range(start, end + 1):
        # Calculate the average fitness for the current generation
        currTrial = 0; currAvg = 0
        while currTrial < numTrials:
            # Get all relevant information
            currGenList, currFitList, currInd = genList[currTrial], fitList[currTrial], indexes[currTrial]

            # If the current pointer is not at the end and if the current generation is greater than or equal to
            # the next optimal generation, increase the index until we are at the next optimal generation
            if currInd < (len(currGenList) - 1) and generation >= currGenList[currInd + 1]:
                indexes[currTrial] += 1
                continue
            
            if debug:
                print(f'({currTrial}, {generation}), ({currInd}, {currGenList[currInd]}, {currFitList[currInd]}), {currGenList}, {currFitList}')

            # Add the current fitness to the current average
            currAvg += currFitList[currInd]
            currTrial += 1
        
        # Calculate the average
        currAvg /= numTrials
        
        # Add the average to the total sum of averages
        totalSum += currAvg

        if generation % step == 0:
            # Add the current generation to the list of generations
            generations.append(generation)
            
            # Take the average of averages and append it
            avgFitnesses.append(totalSum / (generation + 1))

            # Calculate the variance for each point
            var = 0
            for trial in range(numTrials):
                var += (currAvg - fitList[trial][indexes[trial]]) ** 2 / (numTrials - 1)
            variances.append(var)
    
    marginErrors = conf_interval * np.sqrt(variances) / np.sqrt(numTrials)

    return np.array(generations), np.array(avgFitnesses), marginErrors
        
##############################
##    Library Functions     ##
##############################

def getTrapFreq(trap: Union[str, List[int], np.ndarray], func: str = None) -> int:
    ''' Takes in a trap and returns the frequency of that trap with the fitness function '''
    # Open a cursor
    cursor = client.cursor()

    if not func:
        raise Exception('Need to provide a fitness function to search by')
    
    # Standardizing input type
    if not isinstance(trap, str):
        if isinstance(trap, List):
            trap = np.array(trap)
        
        trap = np.array2string(trap)

    frequency = cursor.execute(f' \
        SELECT SUM([frequency]) FROM {FREQ_TABLE} \
        WHERE [function] = :function AND [trap] = :trap;',
        { 'function': func, 'trap': trap }
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

def getTotalCounts(measure: str) -> pd.DataFrame:
    '''
    Returns a data frame where the columns correspond to different fitness functions, and each cell 
    represents the number of traps with a given lethality.
    '''
    # Create a list of series for each of the coherence counts per function
    serList = []

    getSingleCountFunc = getSingleLethalityCount if measure == 'lethality' else getSingleCoherenceCount

    with IncrementalBar(f'{measure} vector map:', max=len(FUNC_VALUES)) as bar:
        for func in FUNC_VALUES:
            serList.append(getSingleCountFunc(func))
            bar.next()
        
    df = pd.concat(serList, axis=1)
    df.fillna(0, inplace=True)
    
    df.rename(
        index={ ind: '%.3f' % ind for ind in df.index },
        columns=FUNC_MAPPINGS,
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

    df = pd.DataFrame(lethPoints).sort_index(axis=1).sort_index(axis=0)

    # Rename dataframe to have column/index names w/ standardized number of digits
    df.rename(columns={ leth: '%.3f' % leth for leth in df.columns }, inplace=True)
    df.rename(index={ coher: '%.3f' % coher for coher in df.index }, inplace=True)

    ## Get proportions
    if df.to_numpy().sum():
        df /= df.to_numpy().sum()

    cursor.close()

    return df

def getOptimalGenerations(func: str, returnFitnesses=False):
    '''
    Returns the generation in which the optimal solution was found for all experiments as
    a list of points ()
    '''
    cursor = client.cursor()

    if func == 'functional':
        filt = 'lethality'
    elif func == 'coherence':
        filt = 'coherence'
    elif func == 'multiobjective':
        filt = 'combined'
    else:
        raise Exception(f'{func} is not a valid function')

    cursor.execute(f' \
        SELECT MIN(tempFreqs.generation) as tempGen, tempFreqs.{filt} \
        FROM ( \
            SELECT trap, generation, trial, {filt} \
            FROM frequencies \
            WHERE [function]=:function \
        ) AS tempFreqs \
        INNER JOIN ( \
            SELECT trap, trial \
            FROM experiments \
            WHERE [function]=:function \
            GROUP BY trap, trial \
        ) AS tempExperiments \
        ON tempExperiments.trap=tempFreqs.trap AND tempExperiments.trial=tempFreqs.trial \
        GROUP BY tempFreqs.trial \
        ORDER BY tempFreqs.trial; \
        ', { 'function': func }
    )

    genList = []
    fitList = []
    for (generation, fitness) in cursor.fetchall():
        genList.append(generation)
        fitList.append(fitness)

    cursor.close()

    if returnFitnesses:
        return np.array(genList), np.array(fitList)
    
    return np.array(genList)

def getAverageOptimalFitness(func: str, start=0, end=10000, step=100):
    ''' Returns a numpy array that contains a vector of generations and average optimal fitnesses '''
    
    if func == 'functional':
        filt = 'lethality'
    elif func == 'coherence':
        filt = 'coherence'
    elif func == 'multiobjective':
        filt = 'combined'
    else:
        raise Exception(f'{func} is not a valid function')

    cursor = client.cursor()
    
    # A list of the generations in which the optimal traps are reached
    numTrials, = cursor.execute(' \
        SELECT MAX([trial]) FROM frequencies WHERE [function]=:function; \
        ', { 'function': func }
    ).fetchone()

    genList = []; fitList = []
    for i in range(numTrials):
        # Get the best trap in the starting generation
        currGen, currFitness = cursor.execute(f' \
            SELECT generation, MAX([{filt}]) FROM frequencies \
            WHERE [function]=:function AND [trial]=:trial AND [generation]=0; \
            ', { 'function': func, 'trial': i + 1 }
        ).fetchone()

        # Lists keeping track of the maximum fitness and its corresponding generation
        currGenList = []
        currFitList = []

        # Get a list of all optimal generations and fitnesses
        while currFitness:
            currGenList.append(currGen)
            currFitList.append(currFitness)

            generation, fitness = cursor.execute(f' \
                SELECT MIN([generation]), MIN([{filt}]) FROM frequencies \
                WHERE [function]=:function AND [trial]=:trial AND [{filt}] > :fitness AND [generation] > :gen; \
                ', { 'function': func, 'fitness': currFitness, 'trial' : i + 1, 'gen': currGen }
            ).fetchone()

            currGen = generation
            currFitness = fitness
    
        genList.append(currGenList)
        fitList.append(currFitList)

    cursor.close()

    return getAverageFitnesses(genList, fitList, start, end, step)

def getCumulativeAverageFitnessAcrossTrials(func: str, start=100, end=10000, stepSize=100):
    '''
    Returns two numpy arrays: one with generation values and another with the corresponding
    average of the relevant fitness function.
    '''
    cursor = client.cursor()

    if func == 'functional':
        filt = 'lethality'
    elif func == 'coherence':
        filt = 'coherence'
    elif func == 'multiobjective':
        filt = 'combined'
    else:
        raise Exception(f'{func} is not a valid function')

    generations = [0]
    fitnessAvgs = [0]
    for i in range(start, end + 1, stepSize):
        avg, = cursor.execute(f'\
            SELECT AVG([{filt}]) FROM frequencies \
            WHERE [function]=:function AND [generation] BETWEEN :lower AND :upper; \
            ', { 'function': func, 'lower': i - start, 'upper': i }
        ).fetchone()

        # Calculate and append the new average, standard deviation, and generation
        fitnessAvgs.append((fitnessAvgs[-1] * generations[-1] + stepSize * avg) / i)
        generations.append(i)

    cursor.close()

    return np.array(generations), np.array(fitnessAvgs)

def getAverageFitnessAcrossTrials(func: str, start=0, end=10000, stepSize=1, conf_interval=1.96):
    '''
    Returns two numpy arrays: one with generation values and another with the corresponding
    average of the relevant fitness function.
    '''
    cursor = client.cursor()

    if func == 'functional':
        filt = 'lethality'
    elif func == 'coherence':
        filt = 'coherence'
    elif func == 'multiobjective':
        filt = 'combined'
    else:
        raise Exception(f'{func} is not a valid function')

    generations = []
    fitnessAvgs = []
    marginErrs = []
    for i in range(start, end + 1, stepSize):
        cursor.execute(f'\
            SELECT {filt}, frequency FROM frequencies \
            WHERE [function]=:function AND [generation]=:generation; \
            ', { 'function': func, 'generation': i }
        ).fetchone()

        fitnesses = [fitness for (fitness, frequency) in cursor.fetchall() for _ in range(frequency)]

        # Calculate and append the new average, standard deviation, and generation
        fitnessAvgs.append(stats.mean(fitnesses))
        generations.append(i)
        marginErrs.append(conf_interval * stats.stdev(fitnesses) / np.sqrt(len(fitnesses)))

    cursor.close()

    return np.array(generations), np.array(fitnessAvgs), np.array(marginErrs)
