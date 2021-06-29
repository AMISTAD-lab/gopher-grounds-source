import csv
import os
from progress.bar import IncrementalBar
from database.client import client
from database.constants import *

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
        (LETH_INDEX, LETH_INDEX_SCHEMA),
        (COHER_INDEX, COHER_INDEX_SCHEMA)
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

def loadFrequencies(inputFile: str, fitnessFunction: str):
    ''' Takes in a frequency csv file as input and loads the data into the database '''
    if not fitnessFunction:
        raise Exception('Need to include the fitness function to insert into {}.'.format(FREQ_TABLE))

    # Open a cursor
    cursor = client.cursor()

    print('Starting to load {} frequencies'.format(fitnessFunction))
    rowCount = 0
    numBars = 1000

    # Get the number of lines in the file
    with open(inputFile, 'r', newline='') as file:
        for i, _ in enumerate(file):
            pass
        rowCount = i - 1
        file.close()

    with IncrementalBar('Processing {} frequencies:'.format(fitnessFunction.lower()), max = numBars) as bar:
        currentBatch = []
        with open(inputFile, 'r', newline='') as out:
            reader = csv.reader(out)

            for i, row in enumerate(reader):
                if i == 0:
                    continue

                # Get the row
                parsedRow = row

                # Cast data types
                parsedRow[1] = int(parsedRow[1])
                parsedRow.append(fitnessFunction)

                currentBatch.append(parsedRow)

                # Commit every 1000 elements and reset batch to limit memory usage
                if i % 1000 == 0:
                    cursor.executemany(
                        'INSERT INTO {} VALUES (?, ?, ?);'.format(FREQ_TABLE),
                        currentBatch
                    )
                    currentBatch = []
                
                # Increment the bar 
                if i % (rowCount // numBars) == 0:
                    bar.next()
            
            # Committing the remainder of the rows that may have not been added
            if currentBatch:
                cursor.executemany(
                    'INSERT INTO {} VALUES (?, ?, ?);'.format(FREQ_TABLE),
                    currentBatch
                )

    print('Committing changes to database...')

    # Commit changes
    client.commit()

    # Complete bar
    bar.finish()

    # Close cursor
    cursor.close()


def loadDatabases(fitnesses=('random', 'coherence', 'functional', 'combined')):
    ''' Inserts all of the compiled csv files into the database '''
    experimentPath = './csv/{}/{}ExperimentData.csv'

    for fitness in fitnesses:
        thresholds = [0.2, 0.4, 0.6, 0.8]

        if fitness == 'functional':
            thresholds.append(1.0)

        loadExperiments(experimentPath.format(fitness, fitness))
        loadFrequencies(thresholds, fitness)
    
    print('Done.')

def setup():
    ''' Sets up all tables and loads the tables with the respective data. '''
    setupTables(overwrite=True)
    loadDatabases()
