# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   PVS_DatabaseHandlerTXD.py
#   Project Valerie - Database Handler for TXD
#
#   Created by Zuki on 20/05/2011.
#   Interface for working with sqlite database
#   
#   Revisions:
#   r6??.Initial - Zuki - Let's import the TXD Interface from database.py
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
import Utf8

#DB_TXD_LOADED = False
#__DB_PATH           = "/hdd/valerie/"
#__DB_PATH           = config.plugins.pvmc.configfolderpath.value #"/hdd/valerie/"

#------------------------------------------------------------------------------------------

gDatabaseHandler = None
gConnection = None

class databaseHandlerTXD(object):
	DB_PATH           = config.plugins.pvmc.configfolderpath.value
	DB_PATH_EPISODES  = config.plugins.pvmc.configfolderpath.value + "episodes/"

	MOVIESTXD  = DB_PATH + "movies.txd"
	TVSHOWSTXD = DB_PATH + "tvshows.txd"

	FAILEDDB   = DB_PATH + "failed.db"

	TXD_VERSION = 3
	
	def __init__(self):
		printl("->", self)
		
	def getInstance(self):
		printl("", self, "D")
		global gDatabaseHandler
		if gDatabaseHandler is None:			
			printl("TXD - New Instance", self)
			gDatabaseHandler = self
		return gDatabaseHandler

#########################################################################

	def getAllMovies(self):
		printl("->", self)
		start_time = time.time()
		records = {}

		try:
			db = Utf8.Utf8(self.MOVIESTXD, "r").read()
			if db is not None:
				lines = db.split("\n")
				version = int(lines[0])
				linesLen = len(lines)
				
				if version >= 3:
					size = 13
				else:
					size = 11
				
				for i in range(1, linesLen, size):
					if lines[i] == "EOF":
						break
					m = MediaInfo()
					m.importDefined(lines[i:i+size], version, True, False, False)
					records[m.Id] = m
					#printl("Movie Id: "+m.Id, self)
					
					#records.add(m)
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (movies.txd): " + str(elapsed_time), self)

		return records

	def getAllSeries(self):
		start_time = time.time()
		records = {}
		try:
			db = Utf8.Utf8(self.TVSHOWSTXD, "r").read()
			if db is not None:
				lines = db.split("\n")
				version = int(lines[0])
				linesLen = len(lines)
				
				if version >= 3:
					size = 11
				else:
					size = 9
				
				records = {}
				for i in range(1, linesLen, size):
					if lines[i] == "EOF":
						break
					m = MediaInfo()
					m.importDefined(lines[i:i+size], version, False, True, False)
					records[m.Id] = m
					printl("serie Id: "+m.Id, self)

					#records.add(m)
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (tvshows.txd): " + str(elapsed_time), self)

		return records
		
	def getEpisodesFromAllSeries(self, series):
		start_time = time.time()
		records = {} # final episodes
		try:	
			for serie in series:
				episodes = self.getEpisodesFromSerie(serie)
				serieKey = serie
				printl("Serie ID: " + str(serieKey), self)
				for episode in episodes:					
					if records.has_key(serieKey) is False:
						records[serieKey] = {}
					media = episodes[episode]
					printl("Serie ID: " + str(serieKey) + "  episode Id: " + str(episode) + "  season: " + str(media.Season) + "  episode: " + str(media.Episode), self)
					if records[serieKey].has_key(media.Season) is False:
						records[serieKey][media.Season] = {}
			
					if records[serieKey][media.Season].has_key(media.Episode) is False:
						records[serieKey][media.Season][media.Episode] = media
			
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		elapsed_time = time.time() - start_time
		printl("Took (episodes/*.txd): " + str(elapsed_time), self)

		return records
		
	def getEpisodesFromSerie(self, serieId):
		start_time = time.time()
		records = {}
		try:	
			db = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + u"episodes/" + serieId + u".txd", "r").read()
			if db is not None:
				lines = db.split("\n")
				version = int(lines[0])
				linesLen = len(lines)
				
				if version >= 3:
					size = 14
				else:
					size = 12
				
				for i in range(1, linesLen, size):
					if lines[i] == "EOF":
						break
					m = MediaInfo()
					m.importDefined(lines[i:i+size], version, False, False, True)
					records[i] = m
					#records.add(m)						
		
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60				
		elapsed_time = time.time() - start_time
		printl("Took (episodes/*.txd): " + str(elapsed_time), self)

		return records

	#def getAllEpisodes(self):
	#	return (self.getEpisodesWithFilter(None))
		
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
		
		return records







	def saveMovies(self, records):		
		printl("->", self)
		start_time = time.time()
		try:		
			f = Utf8.Utf8(self.MOVIESTXD, 'w')
			f.write(unicode(self.TXD_VERSION) + u"\n")
			for movie in records.values():
				f.write(movie.exportDefined(self.TXD_VERSION))
			f.write("EOF\n")
			f.close()
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (movies.txd): " + str(elapsed_time), self)
		
	def saveSeries(self, records):
		
		printl("->", self)
		start_time = time.time()
		try:		
			f = Utf8.Utf8(self.TVSHOWSTXD, 'w')
			f.write(unicode(self.TXD_VERSION) + u"\n")
			for key in records:
				#if self.dbEpisodes.has_key(key): # Check if we have episodes for that serie
				f.write(records[key].exportDefined(self.TXD_VERSION))
			f.write("EOF\n")
			f.close()
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (tvshows.txd): " + str(elapsed_time), self)
		
	def saveEpisodes(self, records):
		
		printl("->", self)
		start_time = time.time()
		try:		
			for serie in records:
				try:
					f = Utf8.Utf8(self.DB_PATH_EPISODES + serie + u".txd", 'w')
					f.write(unicode(self.TXD_VERSION) + u"\n")
					for season in records[serie]:
						for episode in records[serie][season].values():
							f.write(episode.exportDefined(self.TXD_VERSION))
					f.write("EOF\n")
					f.close()
				except Exception, ex: 
					printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")

		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (episodes): " + str(elapsed_time), self)
		
