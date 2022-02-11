import database.setup as dbSetup

dbSetup.setupTables(overwrite=True)
dbSetup.loadFrequencies(['./data/functional.csv', './data/coherence.csv'])

import database.library as dbLib

dbLib.populate_fof('functional', output='./data/functional_fof.csv')
dbLib.populate_fof('coherence', output='./data/coherence_fof.csv')