'''
This file contains the schema for the database, or a constants file for database related structures
'''

EXP_TABLE = 'experiments'
FREQ_TABLE = 'frequencies'
FUNC_INDEX = 'idx_frequencies_func'
LETH_COHER_INDEX = 'idx_frequencies_leth_coher'
COHER_LETH_INDEX = 'idx_frequencies_coher_leth'
GENER_LETH_INDEX = 'idx_frequencies_gener_leth'
GENER_COHER_INDEX = 'idx_frequencies_gener_coher'

EXP_SCHEMA = 'CREATE TABLE {} (\
    trial INTEGER, \
    trap TEXT, \
    function TEXT, \
    fitness REAL, \
    intention INTEGER, \
    lethality REAL, \
    coherence REAL, \
    combined REAL, \
    propDead REAL, \
    stdErr REAL, \
    PRIMARY KEY(function, trap, trial) \
);'.format(EXP_TABLE)

FREQ_SCHEMA = 'CREATE TABLE {} (\
    trial INTEGER, \
    generation INTEGER, \
    trap TEXT, \
    function TEXT, \
    fitness REAL, \
    lethality REAL, \
    coherence REAL, \
    combined REAL, \
    frequency INTEGER DEFAULT 1, \
    PRIMARY KEY(function, trial, generation, trap) \
);'.format(FREQ_TABLE)

FUNC_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (function, trap);'.format(FUNC_INDEX, FREQ_TABLE)

LETH_COHER_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (function, lethality, coherence);'.format(LETH_COHER_INDEX, FREQ_TABLE)

COHER_LETH_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (function, coherence, lethality);'.format(COHER_LETH_INDEX, FREQ_TABLE)

GENER_LETH_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (function, generation, lethality);'.format(GENER_LETH_INDEX, FREQ_TABLE)

GENER_COHER_INDEX_SCHEMA = \
    'CREATE INDEX {} ON {} (function, generation, coherence);'.format(GENER_COHER_INDEX, FREQ_TABLE)
