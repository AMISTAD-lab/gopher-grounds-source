''' Creates an instance of a client to be shared among all database users '''
import pysqlite3 as sqlite3
import numpy as np

# Instantiating database connection
client = sqlite3.connect('/media/amistad-drive1/gopher-data.db')

# Adding adapter for numpy support
sqlite3.register_adapter(np.int32, int)
sqlite3.register_adapter(np.int64, int)
sqlite3.register_adapter(np.float32, int)
sqlite3.register_adapter(np.float64, int)

# Debugging flag
# client.set_trace_callback(print)