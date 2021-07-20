# Constants used in the code base
CELL_ALPHABET = [x for x in range(93)]
DEFAULT_PROB_ENTER = 0.8
MAX_PROB_DEATH = 1 - 0.55 ** 2
ARROW_STRENGTHS = [0, 0.15, 0.3, 0.45]
FUNCTIONS = ['random', 'functional', 'coherence', 'multiobjective', 'binary-distance']

# Total number of traps -> |X|
TOTAL = 427929800129788411

# CSV constants
frequencyHeaders = ['Trial', 'Generation', 'Trap', 'Function', 'Fitness', 'Lethality', 'Coherence', 'Combined']
experimentHeaders = ['Trial', 'Trap', 'Function', 'Fitness', 'Intention', 'Lethality', 'Coherence', 'Combined', 'PropDead', 'StdErr']
fofHeaders = ['Frequency', 'FrequencyOfFrequency']

# File paths
experimentPath = './experiments/{}{}.csv'
frequencyPath = './frequencies/{}{}.csv'
fofPath = './frequencies/{}{}FoF.csv'
realExperimentPath = './realExperiments/{}/{}{}.{}'

# Enumeration of possible lethality/coherence values and generation ranges
lethalities = sorted([
    round((1 - (1 - i) * (1 - j)) / MAX_PROB_DEATH, 4)
    for i in ARROW_STRENGTHS
    for j in ARROW_STRENGTHS
    if i <= j
])

coherences = sorted(
    list(
        {
            round(i / j, 4)
            for i in range(0, 11)
            for j in range(1, 10)
            if i / j <= 10 / 9
        }
    )
)

generations = ['0-999', *[f'{i}000-{i}999'for i in range(1, 11)]]
