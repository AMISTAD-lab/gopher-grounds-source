''' To load the database and generate all visuals, run this script file '''

import database.setup as dbSetup
import scripts.plotScript as plot
import geneticAlgorithm.constants as constants

dbSetup.loadFrequencies([constants.getFrequencyPath('uniform-random', f'_new_enc_{i}') for i in range(1, 121)])
plot.generate_all_visuals()