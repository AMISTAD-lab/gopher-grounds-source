''' To load the database and generate all visuals, run this script file '''

import database.setup as dbSetup
import scripts.plotScript as plot

dbSetup.setup()
plot.generate_all_visuals()