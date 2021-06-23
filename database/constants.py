'''
This file contains the schema for the database, or a constants file for database related structures
'''

EXP_TABLE = 'experiments'
FREQ_TABLE = 'frequencies'
FUNC_INDEX = 'idx_frequencies_func'
LETH_INDEX = 'idx_frequencies_lethality'
COHER_INDEX = 'idx_frequencies_coherence'

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
    lethality REAL, \
    coherence REAL, \
    threshold REAL, \
    fitnessFunc TEXT, \
    PRIMARY KEY(trap, fitnessFunc, threshold) \
);'.format(FREQ_TABLE)

FUNC_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (fitnessFunc, trap);'.format(FUNC_INDEX, FREQ_TABLE)

LETH_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (lethality, threshold);'.format(LETH_INDEX, FREQ_TABLE)

COHER_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (coherence, threshold);'.format(COHER_INDEX, FREQ_TABLE)
