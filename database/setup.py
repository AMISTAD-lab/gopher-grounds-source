import csv
import os
from typing import List
from progress.bar import IncrementalBar
from database.client import client
from database.constants import *
import geneticAlgorithm.fitnessFunctions as functions
import geneticAlgorithm.encoding as encoding

def exists(tableName: str, type: str):
    ''' Returns true if a table with the given tableName exists '''
    cursor = client.cursor()

    queryData = {
        'type': type,
        'name': tableName
    }

    exists = cursor.execute(
        'SELECT name FROM sqlite_master WHERE type=:type and name=:name', 
        queryData
    ).fetchone()

    cursor.close()
    return bool(exists)

def setupTables(overwrite = False):
    '''
    Sets up a new set of tables for experiments and frequencies. If tables already exist, then
    they will be overwritten unless otherwise argued.
    '''
    cursor = client.cursor()

    if overwrite:
        cursor.execute('DROP TABLE IF EXISTS {};'.format(EXP_TABLE))
        cursor.execute('DROP TABLE IF EXISTS {};'.format(FREQ_TABLE))
        cursor.execute('DROP INDEX IF EXISTS {};'.format(FREQ_INDEX))

        cursor.execute(EXP_SCHEMA)
        cursor.execute(FREQ_SCHEMA)
        cursor.execute(FREQ_INDEX_SCHEMA)
        client.commit()
        return
    
    if not exists(EXP_TABLE, 'table'):
        cursor.execute(EXP_SCHEMA)
    
    if not exists(FREQ_TABLE, 'table'):
        cursor.execute(FREQ_SCHEMA)
    
    if not exists(FREQ_INDEX, 'index'):
        cursor.execute(FREQ_INDEX_SCHEMA)
    
    # Commit changes
    client.commit()

    # Close cursor
    cursor.close()

def loadExperiments(inputFile: str):
    ''' Takes an input file (as csv) and loads all the data from the CSV into the database '''
    # Open a cursor
    cursor = client.cursor()

    currentBatch = []
    with open(inputFile, 'r') as out:
        reader = csv.reader(out)
        for i, row in enumerate(reader):
            if i == 0:
                continue

            # Get the row
            parsedRow = row[1:]

            # Cast data types
            parsedRow[1] = float(parsedRow[1])
            parsedRow[3] = float(parsedRow[3])
            parsedRow[4] = float(parsedRow[4])
            parsedRow[6] = 1 if parsedRow[6] == 'True' else 0
            parsedRow[7] = float(parsedRow[7])

            currentBatch.append(parsedRow)

            # Commit every 1000 elements and reset batch
            if i % 1000 == 0:
                cursor.executemany(
                    'INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?);'.format(EXP_TABLE),
                    currentBatch
                )
                currentBatch = []

    # Commit changes
    client.commit()

    # Close cursor
    cursor.close()

def loadFrequencies(thresholds: str, fitnessFunction: str):
    ''' Takes in a frequency csv file as input and loads the data into the database '''
    if not fitnessFunction:
        raise Exception('Need to include the fitness function to insert into {}.'.format(FREQ_TABLE))

    # Open a cursor
    cursor = client.cursor()

    print('Starting to load {} frequencies'.format(fitnessFunction))
    rowCount = 0
    numBars = 1000

    # Create a template with the fitness function pre-populated, and the other variables populated later
    pathTemplate = './frequencies/{func}/{func}{{}}Thresh{{}}Freqs.csv'.format(func = fitnessFunction)

    # Create all pairs of intentions and thresholds if the file exists
    pairs = [
        (intent, thresh)
        for thresh in thresholds
        for intent in ('NoIntention', 'Intention')
        if os.path.exists(pathTemplate.format(intent, thresh))
    ]

    # Get row count
    for intent, thresh in pairs:
        inputFile = pathTemplate.format(intent, thresh)

        with open(inputFile, 'r') as out:
            reader = csv.reader(out)
            for i, _ in enumerate(reader):
                continue
            rowCount += i

    count = 0
    with IncrementalBar('Processing {} frequencies:'.format(fitnessFunction.lower()), max = numBars) as bar:
        # Takes in a string representation of a list and makes it an encoding
        createEncoding = lambda x: [
            int(digit.strip())
            for digit in x[1:-1].split(' ')
            if digit
        ]

        for intent, thresh in pairs:
            inputFile = pathTemplate.format(intent, thresh)
            
            currentBatch = []
            with open(inputFile, 'r') as out:
                reader = csv.reader(out)

                for i, row in enumerate(reader):
                    if i == 0:
                        continue

                    # Get the row
                    parsedRow = row

                    # Cast data types
                    parsedRow[1] = int(parsedRow[1])
                    parsedRow.append(fitnessFunction)

                    trap = encoding.singleDecoding(createEncoding(parsedRow[0]))

                    parsedRow.append(functions.functionalFitness(trap))
                    parsedRow.append(functions.coherentFitness(trap))
                    parsedRow.append(thresh)

                    currentBatch.append(parsedRow)

                    # Commit every 1000 elements and reset batch to limit memory usage
                    if count % 1000 == 0:
                        cursor.executemany(
                            'INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?);'.format(FREQ_TABLE),
                            currentBatch
                        )
                        currentBatch = []
                    
                    # Increment the bar 
                    if count % (rowCount // numBars) == 0:
                        bar.next()

                    count += 1
                
                # Committing the remainder of the rows that may have not been added
                if currentBatch:
                    cursor.executemany(
                        'INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?);'.format(FREQ_TABLE),
                        currentBatch
                    )

        print()
        print('Committing changes to database...')

        # Commit changes
        client.commit()

        # Complete bar
        bar.finish()

        # Close cursor
        cursor.close()

        count += 1

def loadDatabases(fitnesses=('random', 'coherence', 'functional', 'combined')):
    ''' Inserts all of the compiled csv files into the database '''
    experimentPath = './csv/{}/{}ExperimentData.csv'

    for fitness in fitnesses:
        thresholds = [0.2, 0.4, 0.6, 0.8]

        if fitness == 'functional':
            thresholds.append(1)

        loadExperiments(experimentPath.format(fitness, fitness))
        loadFrequencies(thresholds, fitness)
    
    print('Done.')

def setup():
    ''' Sets up all tables and loads the tables with the respective data. '''
    setupTables(overwrite=True)
    loadDatabases()
