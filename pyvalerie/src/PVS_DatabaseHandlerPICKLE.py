# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   PVS_DatabaseHandlerPICKLE.py
#   Project Valerie - Database Handler for PICKLE
#
#   Created by Zuki on 20/05/2011.
#   Interface for working with PICKLE Files
#   
#   Revisions:
#   r7??.Initial - Zuki - Let's import the Pickle Interface from database.py
#
#   r
#
#   r
#
#   r
#
#   r
#
#   r
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import time
import cPickle   as pickle
from Components.config import config
from   MediaInfo         import MediaInfo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#DB_TXD_LOADED = False
#__DB_PATH           = "/hdd/valerie/"
#__DB_PATH           = config.plugins.pvmc.configfolderpath.value #"/hdd/valerie/"

#------------------------------------------------------------------------------------------

gDatabaseHandler = None
gConnection = None

class databaseHandlerPICKLE(object):
	DB_PATH           = config.plugins.pvmc.configfolderpath.value

	FAILEDDB   = DB_PATH + "failed.db"
	MOVIESDB   = DB_PATH + "movies.db"
	TVSHOWSDB  = DB_PATH + "tvshows.db"
	EPISODESDB = DB_PATH + "episodes.db"

	def __init__(self):
		printl("->", self)
		
	def getInstance(self):
		printl("", self, "D")
		global gDatabaseHandler
		if gDatabaseHandler is None:			
			printl("PICKLE - New Instance", self)
			gDatabaseHandler = self
		return gDatabaseHandler

#########################################################################

	def getAllMovies(self):
		printl("->", self)
		start_time = time.time()
		records = {}
		try:		
			fd = open(self.MOVIESDB, "rb")
			records = pickle.load(fd)
			fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (movies.db): " + str(elapsed_time), self)
		
		return (records)
		
	def getAllSeries(self):
		start_time = time.time()
		try:
			fd = open(self.TVSHOWSDB, "rb")
			records = {}
			records = pickle.load(fd)
			fd.close()
				
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (tvshows.db): " + str(elapsed_time), self)
		
		return (records)

	def getAllEpisodes(self):
		start_time = time.time()
		records = {}
		try:
			fd = open(self.EPISODESDB, "rb")
			records = pickle.load(fd)
			fd.close()
		
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (episodes.db): " + str(elapsed_time), self)

		return (records)


	def getFailedFiles(self):
		printl("->", self)
		start_time = time.time()
		records = {}
		try:		
			fd = open(self.FAILEDDB, "rb")
			records = pickle.load(fd)
			fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (failed.db): " + str(elapsed_time), self)
		
		return (records)


	def saveMovies(self, records):
		
		printl("->", self)
		start_time = time.time()
		try:		
			fd = open(self.MOVIESDB, "wb")
			pickle.dump(records, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (movies.db): " + str(elapsed_time), self)
		
	def saveSeries(self, records):
		
		printl("->", self)
		start_time = time.time()
		try:		
			fd = open(self.TVSHOWSDB, "wb")
			pickle.dump(records, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (tvshows.db): " + str(elapsed_time), self)
		
	def saveEpisodes(self, records):
		
		printl("->", self)
		start_time = time.time()
		try:		
			fd = open(self.EPISODESDB, "wb")
			pickle.dump(records, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (episodes.db): " + str(elapsed_time), self)
		
