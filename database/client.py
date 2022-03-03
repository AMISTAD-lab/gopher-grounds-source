''' Creates an instance of a client to be shared among all database users '''
import numpy as np

# allowing for cross compatability on both lab and local machines
import sqlite3 as sqlite3

db_file = './gopher-data.db'

# if the sqlite version is lower than needed, then we change to lab environment
if sqlite3.version == '2.6.0':
    import pysqlite3 as sqlite3
    db_file = '/media/amistad-drive1/gopher-data.db'

# Instantiating database connection
client = sqlite3.connect(db_file)

# Adding adapter for numpy support
sqlite3.register_adapter(np.int32, int)
sqlite3.register_adapter(np.int64, int)
sqlite3.register_adapter(np.float32, int)
sqlite3.register_adapter(np.float64, int)

# Debugging flag
# client.set_trace_callback(print)