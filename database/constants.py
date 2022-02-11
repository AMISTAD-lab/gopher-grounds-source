'''
This file contains the schema for the database, or a constants file for database related structures
'''

# Table names
EXP_TABLE = 'experiments'
FREQ_TABLE = 'frequencies'
FOF_TABLE = 'fof'

# Indexes
FUNC_INDEX = 'idx_frequencies_func'
LETH_COHER_INDEX = 'idx_frequencies_leth_coher'
COHER_LETH_INDEX = 'idx_frequencies_coher_leth'
GENER_INDEX = 'idx_frequencies_gener'

# Partial Indexes
LETH_INDEX = 'idx_frequencies_leth'
COHER_INDEX = 'idx_frequencies_coher'
COMBINED_INDEX = 'idx_frequencies_combined'

EXP_SCHEMA = f'CREATE TABLE {EXP_TABLE} (\
    experiment INTEGER, \
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
    PRIMARY KEY(function, trap, experiment) \
);'

FREQ_SCHEMA = f'CREATE TABLE {FREQ_TABLE} (\
    trial INTEGER, \
    generation INTEGER, \
    trap TEXT, \
    function TEXT, \
    fitness REAL, \
    lethality REAL, \
    coherence REAL, \
    combined REAL, \
    generationRange INTEGER, \
    frequency INTEGER DEFAULT 1, \
    PRIMARY KEY(function, trial, generation, trap) \
);'

FOF_SCHEMA = f'CREATE TABLE {FOF_TABLE} (\
    function TEXT, \
    frequency INTEGER, \
    fof INTEGER, \
    PRIMARY KEY(function, frequency) \
);'

FUNC_INDEX_SCHEMA = \
    f'CREATE INDEX {FUNC_INDEX} ON {FREQ_TABLE} ([function], [trap], [trial], [generation]);'

LETH_COHER_INDEX_SCHEMA = \
    f'CREATE INDEX {LETH_COHER_INDEX} ON {FREQ_TABLE} ([function], [lethality], [coherence]);'

COHER_LETH_INDEX_SCHEMA = \
    f'CREATE INDEX {COHER_LETH_INDEX} ON {FREQ_TABLE} ([function], [coherence]);'

GENER_INDEX_SCHEMA = \
    f'CREATE INDEX {GENER_INDEX} ON {FREQ_TABLE} ([function], [generation]);'

LETH_INDEX_SCHEMA = \
    f'CREATE INDEX {LETH_INDEX} ON {FREQ_TABLE} ([function], [trial], [generation], [lethality]) WHERE [function]="functional";'

COHER_INDEX_SCHEMA = \
    f"CREATE INDEX idx_frequencies_coher ON frequencies ([function], [trial], [generation], [coherence]) WHERE [function]='coherence';"

COMBINED_INDEX_SCHEMA = \
    f'CREATE INDEX {COMBINED_INDEX} ON {FREQ_TABLE} ([function], [trial], [generation], [combined]) WHERE [function]="multiobjective";'

FUNC_VALUES = ['random', 'uniform-random', 'binary-distance', 'coherence', 'functional', 'multiobjective', 'designed']

FUNC_MAPPINGS = {
    'random': 'random',
    'functional': 'funct',
    'coherence': 'coher',
    'multiobjective': 'multi',
    'binary-distance': 'hamming',
    'uniform-random': 'unif',
    'designed': 'desig'
}
