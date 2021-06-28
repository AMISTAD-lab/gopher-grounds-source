'''
This file contains the schema for the database, or a constants file for database related structures
'''

EXP_TABLE = 'experiments'
FREQ_TABLE = 'frequencies'

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
    PRIMARY KEY(trap, fitnessFunc) \
);'.format(FREQ_TABLE)