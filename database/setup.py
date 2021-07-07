import csv
import os
from progress.bar import IncrementalBar
from database.client import client
from database.constants import *
import geneticAlgorithm.constants as constants

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

    tables = [(EXP_TABLE, EXP_SCHEMA), (FREQ_TABLE, FREQ_SCHEMA)]
    indexes = [
        (FUNC_INDEX, FUNC_INDEX_SCHEMA),
        (LETH_COHER_INDEX, LETH_COHER_INDEX_SCHEMA),
        (COHER_LETH_INDEX, COHER_LETH_INDEX_SCHEMA)
    ]

    if overwrite:
        for (table, schema) in tables:
            cursor.execute('DROP TABLE IF EXISTS {};'.format(table))
            cursor.execute(schema)

        for (index, schema) in indexes:
            cursor.execute('DROP INDEX IF EXISTS {};'.format(index))
            cursor.execute(schema)

        client.commit()

        return
    
    for (table, schema) in tables:
        if not exists(table, 'table'):
            cursor.execute(schema)
    
    for (index, schema) in indexes:
        if not exists(index, 'index'):
            cursor.execute(schema)
    
    client.commit()
    cursor.close()

def loadExperiments(inputFile: str):
    ''' Takes an input file (as csv) and loads all the data from the CSV into the database '''
    # Open a cursor
    cursor = client.cursor()

    currentBatch = []
    with open(inputFile, 'r', newline='') as out:
        reader = csv.reader(out)
        for i, row in enumerate(reader):
            if i == 0:
                continue

            # Cast data types
            row[0] = int(row[0])
            row[3] = float(row[3])
            row[4] = int(row[4])
            row[5] = float(row[5])
            row[6] = float(row[6])
            row[7] = float(row[7])
            row[8] = float(row[8])
            row[9] = float(row[9])

            currentBatch.append(row)

            # Commit every 1000 elements and reset batch
            if i % 1000 == 0:
                cursor.executemany(
                    'INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'.format(EXP_TABLE),
                    currentBatch
                )
                currentBatch = []

    # Commit changes
    client.commit()

    # Close cursor
    cursor.close()

def loadFrequencies(inputFile: str):
    ''' Takes in a frequency csv file as input and loads the data into the database '''
    # Open a cursor
    cursor = client.cursor()

    print('Starting to load frequencies from {}.'.format(inputFile.split('/')[-1]))
    rowCount = 0
    numBars = 1000
    barSkip = 1

    # Get the number of lines in the file
    with open(inputFile, 'r', newline='') as file:
        for i, _ in enumerate(file):
            pass
        rowCount = i - 1
        file.close()

    modulo = rowCount // numBars
    if not modulo:
        modulo = 1
        barSkip = numBars // rowCount

    with IncrementalBar('Processing:', max = numBars) as bar:
        currentBatch = []
        with open(inputFile, 'r', newline='') as out:
            reader = csv.reader(out)

            for i, row in enumerate(reader):
                if i == 0:
                    continue

                # Cast data types
                row[0] = int(row[0])

                # Making generation an enum to speed up query
                row[1] = int(row[1])
                row[1] = row[1] // 1000 if row[1] < 1e4 else 9

                row[4] = float(row[4])
                row[5] = float(row[5])
                row[6] = float(row[6])
                row[7] = float(row[7])

                currentBatch.append(row)

                # Commit every 1000 elements and reset batch to limit memory usage
                if i % 1000 == 0:
                    cursor.executemany(
                        'INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1) \
                        ON CONFLICT DO UPDATE SET frequency = frequency + 1;'.format(FREQ_TABLE),
                        currentBatch
                    )
                    currentBatch = []
                
                # Increment the bar 
                if i % modulo == 0:
                    bar.next(n=barSkip)
            
            # Committing the remainder of the rows that may have not been added
            if currentBatch:
                cursor.executemany(
                    'INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1) \
                    ON CONFLICT DO UPDATE SET frequency = frequency + 1;'.format(FREQ_TABLE),
                    currentBatch
                )

    print('Committing changes to database...')

    # Commit changes
    client.commit()

    # Complete bar
    bar.finish()

    # Close cursor
    cursor.close()


def loadDatabases(fitnesses=('random', 'coherence', 'functional', 'multiobjective', 'designed')):
    ''' Inserts all of the compiled csv files into the database '''
    experimentPath = constants.experimentPath
    frequencyPath = constants.frequencyPath

    for fitness in fitnesses:
        loadExperiments(experimentPath.format(fitness))
        loadFrequencies(frequencyPath.format(fitness))
    
    print('Done.')

def setup():
    ''' Sets up all tables and loads the tables with the respective data. '''
    setupTables(overwrite=True)
    loadDatabases()
