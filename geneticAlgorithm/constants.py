CELL_ALPHABET = [x for x in range(93)]
DEFAULT_PROB_ENTER = 0.8

# Total number of traps -> |X|
TOTAL = 427929800129788411

# CSV constants
frequencyHeaders = ['Trial', 'Generation', 'Trap', 'Function', 'Lethality', 'Coherence']
experimentHeaders = ['Trial', 'Trap', 'Function', 'Fitness', 'Intention', 'Lethality', 'Coherence', 'PropDead', 'StdErr']
fofHeaders = ['Frequency', 'FrequencyOfFrequency']

# File paths
experimentPath = './csv/{}{}.csv'
frequencyPath = './frequencies/{}{}.csv'
fofPath = './frequencies/{}{}FoF.csv'
