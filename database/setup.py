import csv
from progress.bar import IncrementalBar
from database.client import client
from database.constants import *

def tableExists(tableName: str):
    cursor = client.cursor()
    '''
    Returns true if a table with the given tableName exists
    '''
    queryData = {
        'type': 'table',
        'name': tableName
    }

    isTable = cursor.execute(
        'SELECT name FROM sqlite_master WHERE type=:type and name=:name', 
        queryData
    ).fetchone()

    cursor = client.cursor()
    return bool(isTable)

def setupTables(overwrite = False):
    '''
    Sets up a new set of tables for experiments and frequencies. If tables already exist, then
    they will be overwritten unless otherwise argued.
    '''
    cursor = client.cursor()

    if overwrite:
        cursor.execute('DROP TABLE IF EXISTS {};'.format(EXP_TABLE))
        cursor.execute('DROP TABLE IF EXISTS {};'.format(FREQ_TABLE))
        cursor.execute(EXP_SCHEMA)
        cursor.execute(FREQ_SCHEMA)
        client.commit()
        return
    
    if not tableExists(EXP_TABLE):
        cursor.execute(EXP_SCHEMA)
    
    if not tableExists(FREQ_TABLE):
        cursor.execute(FREQ_SCHEMA)
    
    # Commit changes
    client.commit()

    # Close cursor
    cursor.close()

def loadExperiments(inputFile):
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

def loadFrequencies(inputFile: str, fitnessFunction: str):
    ''' Takes in a frequency csv file as input and loads the data into the database '''
    if not fitnessFunction:
        raise Exception('Need to include the fitness function to insert into {}.'.format(FREQ_TABLE))

    # Open a cursor
    cursor = client.cursor()

    print('Starting to load {} frequencies'.format(fitnessFunction))
    rowCount = 0

    # Get the number of lines in the file
    with open(inputFile) as file:
        for i, _ in enumerate(file):
            pass
        rowCount = i - 1
        file.close()

    with IncrementalBar('Processing {} frequencies:'.format(fitnessFunction.lower()), max = int(rowCount / 10000)) as bar:
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

                currentBatch.append(parsedRow)

                # Commit every 1000 elements and reset batch to limit memory usage
                if i % 10000 == 0:
                    bar.next()
                    cursor.executemany(
                        'INSERT INTO {} VALUES (?, ?, ?);'.format(FREQ_TABLE),
                        currentBatch
                    )
                    currentBatch = []
            
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
    frequencyPath = './frequencies/{}/{}FreqsCompiled.csv'

    for fitness in fitnesses:
        loadExperiments(experimentPath.format(fitness, fitness))
        loadFrequencies(frequencyPath.format(fitness, fitness), fitness)
    
    print('Done.')

def setup():
    ''' Sets up all tables and loads the tables with the respective data. '''
    setupTables(overwrite=True)
    loadDatabases()