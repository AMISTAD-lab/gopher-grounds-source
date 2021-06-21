''' Creates an instance of a client to be shared among all database users '''
import sqlite3

# Instantiating database connection
client = sqlite3.connect('gopher-data.db')