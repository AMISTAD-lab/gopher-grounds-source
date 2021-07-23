import csv
import os
from typing import List
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
        (COHER_LETH_INDEX, COHER_LETH_INDEX_SCHEMA),
        (GENER_INDEX, GENER_INDEX_SCHEMA),
        (LETH_INDEX, LETH_INDEX_SCHEMA),
        (COHER_INDEX, COHER_INDEX_SCHEMA),
        (COMBINED_INDEX, COMBINED_INDEX_SCHEMA),
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

def wrangleExperimentCSV(inputFiles: List[str]):
    ''' Ensures that the experiment CSV files are in the correct format '''
    for inputFile in inputFiles:
        new_file = []
        with open(inputFile, 'r', newline='') as out:
            reader = csv.reader(out)
            for i, row in enumerate(reader):
                if i == 0:
                    if row[0] == 'Experiment':
                        break
                    new_file.append(['Experiment', *row])
                    continue
            
                new_file.append([i, int(row[0]) // 2 + 1, *row[1:]])
        
        if new_file:
            with open(inputFile, 'w+', newline='') as out:
                csv.writer(out).writerows(new_file)
        
        new_file = []

def loadExperiments(inputFiles: str):
    ''' Takes an input file (as csv) and loads all the data from the CSV into the database '''
    # Open a cursor
    cursor = client.cursor()

    wrangleExperimentCSV(inputFiles)

    currentBatch = []; currTrial = 1
    for inputFile in inputFiles:
        with open(inputFile, 'r', newline='') as out:
            reader = csv.reader(out)
            for i, row in enumerate(reader):
                if i == 0:
                    continue

                # Cast data types
                # Each file starts at 1 so we calculate the offset
                row[0] = currTrial
                row[1] = (int(row[0]) + 1) // 2
                row[4] = float(row[4])
                row[5] = int(row[5])
                row[6] = float(row[6])
                row[7] = float(row[7])
                row[8] = float(row[8])
                row[9] = float(row[9])
                row[10] = float(row[10])

                currentBatch.append(row)
            
                currTrial += 1

    # Insert all elements into the database
    cursor.executemany(
        'INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'.format(EXP_TABLE),
        currentBatch
    )

    client.commit()
    cursor.close()

def loadFrequencies(inputFiles: str):
    ''' Takes in a frequency csv file as input and loads the data into the database '''
    # Open a cursor
    cursor = client.cursor()

    trial_num = 1; prev_trial = 1
    with IncrementalBar('Processing:', max = len(inputFiles)) as bar:
        for inputFile in inputFiles:
            currentBatch = []
            with open(inputFile, 'r', newline='') as out:
                reader = csv.reader(out)

                for i, row in enumerate(reader):
                    if i == 0:
                        continue

                    # Cast data types
                    if prev_trial != int(row[0]):
                        prev_trial = int(row[0])
                        trial_num += 1
                    
                    row[0] = trial_num
                    row[1] = int(row[1])

                    row[4] = float(row[4])
                    row[5] = float(row[5])
                    row[6] = float(row[6])
                    row[7] = float(row[7])

                    # Adding generation range to the results
                    row.append(row[1] // 1000 if row[1] < 1e4 else 9)
                    currentBatch.append(row)
                
            # Committing all rows from the file to the database
            cursor.executemany(
                'INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1) \
                ON CONFLICT DO UPDATE SET frequency = frequency + 1;'.format(FREQ_TABLE),
                currentBatch
            )
            
            # Increment the bar
            bar.next()

    print('Committing changes to database...')

    # Commit changes
    client.commit()
    cursor.close()
    bar.finish()

def loadDatabases(fitnesses=('random', 'coherence', 'functional', 'multiobjective', 'binary-distance', 'uniform-random', 'designed'), num_files=5):
    ''' Inserts all of the compiled csv files into the database '''
    experimentPath = constants.experimentPath
    frequencyPath = constants.frequencyPath

    for fitness in fitnesses:
        experiment_file_paths = []
        frequency_file_paths = []
        for i in range(num_files):
            currExpPath = experimentPath.format(enc='new_encoding', func=fitness, suff=f'_new_enc_{i + 1}')
            currFreqPath = frequencyPath.format(enc='new_encoding', func=fitness, suff=f'_new_enc_{i + 1}')

            if not os.path.exists(currExpPath) and fitness != 'uniform-random':
                print(f'Cannot load {fitness} experiment since {currExpPath} does not exist.')
            
            if not os.path.exists(currFreqPath) and fitness != 'uniform-random':
                print(f'Cannot load {fitness} frequencies since {currFreqPath} does not exist.')

            experiment_file_paths.append(currExpPath)
            frequency_file_paths.append(currFreqPath)

        # loadExperiments(experiment_file_paths)
        loadFrequencies(frequency_file_paths)
    
    print('Done.')

def setup():
    ''' Sets up all tables and loads the tables with the respective data. '''
    setupTables(overwrite=True)
    loadDatabases()
