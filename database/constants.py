'''
This file contains the schema for the database, or a constants file for database related structures
'''

EXP_TABLE = 'experiments'
FREQ_TABLE = 'frequencies'
FREQ_INDEX = 'idx_frequencies_freq'

EXP_SCHEMA = 'CREATE TABLE {} (\
    trap TEXT PRIMARY KEY, \
    fitness REAL, \
    fitnessFunc TEXT, \
    propDead REAL, \
    stdErr REAL, \
    confInt TEXT, \
    intention INTEGER, \
    threshold REAL \
);'.format(EXP_TABLE)

FREQ_SCHEMA = 'CREATE TABLE {} (\
    trap TEXT, \
    frequency INTEGER, \
    fitnessFunc TEXT, \
    function REAL, \
    coherence REAL, \
    threshold REAL, \
    PRIMARY KEY(trap, fitnessFunc) \
);'.format(FREQ_TABLE)

FREQ_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (fitnessFunc, frequency)'.format(FREQ_INDEX, FREQ_TABLE)
