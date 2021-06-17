import sqlite3

''' Creates an instance of a client to be shared among all database users '''

# Instantiating database connection
client = sqlite3.connect('gopher-data.db')