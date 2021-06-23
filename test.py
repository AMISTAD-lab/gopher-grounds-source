import database.setup as dbsetup

dbsetup.setupTables(overwrite=True)
dbsetup.loadDatabases(("functional","coherence", "random"))