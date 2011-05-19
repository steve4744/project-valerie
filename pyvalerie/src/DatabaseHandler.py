import os

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

DB_SQLITE_LOADED = False
DB_PATH           = "/hdd/valerie/"

if os.path.exists(DB_PATH + "usesql"):	
	printl("easter egg found :)))")
	try:
		#from sqlite3 import dbapi2 as sql
		import sqlite3 as sql
		DB_SQLITE_LOADED = True
	except:
		printl("Exception: No SQLite installed ??? : ")
else:
    printl("NO easter egg found :(( ... create a file named 'usesql' on " + DB_PATH )

#------------------------------------------------------------------------------------------

gConnection = None
gDatabaseHandler = None

class databaseHandler(object):

	DB_SQLITE_ACTIVE  = False
	DB_SQLITE_LOADED  = False
	DB_SQL_FILENAME   = "valerie.db"
	DB_PATH           = "/hdd/valerie/"

	def __init__(self):
		printl("->", self)
		self.DB_SQLITE_LOADED = DB_SQLITE_LOADED 
		printl("<-", self)
				    
				    
	def getInstance(self):
		printl("", self, "D")
		global gDatabaseHandler
		if gDatabaseHandler is None:
			gDatabaseHandler = self
			printl("New Instance", self)
		
		return gDatabaseHandler

	def OpenDatabase(self):
		connectstring = self.DB_PATH + self.DB_SQL_FILENAME
		# make connection string variable over Config
		db_exists = False
		
		if os.path.exists(connectstring):
			db_exists = True
		try:
			global gConnection
			if gConnection is None:
				gConnection = sql.connect(connectstring) #connectstring)
				printl("New Connection", self)
				if not os.access(connectstring, os.W_OK):
					printl("[Project Valerie] Error: database file needs to be writable, can not open %s for writing..." % connectstring)
					gConnection.close()
					return None
							
		except Exception, ex:
			printl("[Project Valerie] unable to open database file: %s" % connectstring)
			printl(str(ex))
			return None

		if not db_exists :
			#connection.execute('BEGIN TRANSACTION;')
			gConnection.execute('CREATE TABLE IF NOT EXISTS Media    (Media_id INTEGER NOT NULL, Imdb_Id TEXT, thetvdb_id TEXT, Title TEXT, Tag TEXT, Plot TEXT, Runtime INTEGER, Popularity INTEGER, genre_id INTEGER, Year INTEGER, Month INTEGER, Day INTEGER, Path TEXT, Filename TEXT, Extension TEXT, MediaType INTEGER, PRIMARY KEY(Media_id));')
			gConnection.execute('CREATE TABLE IF NOT EXISTS Episodes (Media_id INTEGER NOT NULL, Episode_id INTEGER NOT NULL, Serie_Id INTEGER, thetvdb_id INTEGER, Title TEXT, Episode INTEGER, Plot TEXT, Runtime INTEGER, Popularity INTEGER, genre_id INTEGER, Year INTEGER, Month INTEGER, Day INTEGER, Path TEXT, Filename TEXT, Extension TEXT, PRIMARY KEY(Media_id, Episode_id));')
			#connection.execute('CREATE TABLE IF NOT EXISTS Genre (Genre_id INTEGER NOT NULL, genre_text TEXT, PRIMARY KEY(Genre_id));')
			#connection.execute('CREATE TABLE IF NOT EXISTS Genre_Loc (Genre_id INTEGER NOT NULL, location TEXT NOT NULL, genre_text TEXT, PRIMARY KEY(Genre_id, location));')
			#connection.execute('COMMIT;')

			printl("Database created")
			
		return gConnection

	## executes the given statement with substitution variables
	def commit(self):
		connection = self.OpenDatabase()
		if connection is not None:
			connection.commit() 
	
	## executes the given statement
	def queryExecute(self, sqlSatement):
		connection = self.OpenDatabase()
		if connection is not None:
			try:
				cursor = connection.cursor()
				cursor.execute(sqlSatement)
				cursor.close()
				connection.commit() 
				return True
			except sql.IntegrityError, ex:
				printl(str(ex))
				return False

			#connection.close()

	## executes the given statement with substitution variables
	def queryInsert(self, sqlStatement, args):
		connection = self.OpenDatabase()
		if connection is not None:
			try:
				cursor = connection.cursor()
				cursor.execute(sqlStatement, args)
				cursor.close()
			#	connection.commit() 
				return True
			except sql.IntegrityError, ex:
				printl(str(ex))
				return False
			#connection.close()


