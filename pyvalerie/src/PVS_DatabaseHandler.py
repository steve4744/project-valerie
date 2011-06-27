# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   PVS_DatabaseHandler.py
#   Project Valerie - Database Handler
#
#   Created by user on 01/01/1900.
#   Interface for working with databases
#   
#   Revisions:
#   r000.Initial - Zuki - renamed from database.py
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

import cPickle   as pickle
from   datetime import date
import os
from threading import Lock
import time

from Components.config import config

import Config
import DirectoryScanner
from   FailedEntry       import FailedEntry
import Genres
from   MediaInfo         import MediaInfo
import Utf8

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
	
DB_SQLITE_LOADED = False

try:
	from Plugins.Extensions.ProjectValerieSync.PVS_DatabaseHandlerSQL import databaseHandlerSQL
	#from PVS_DatabaseHandlerSQL import databaseHandlerSQL
	DB_SQLITE_LOADED = True
	printl("PVS_DatabaseHandlerSQL Loaded    :) ", None, "W")	
except Exception, ex:
	printl("Exception: PVS_DatabaseHandlerSQL not Loaded :(   "+ str(ex), None, "W")
		
try:					   
	from Plugins.Extensions.ProjectValerieSync.PVS_DatabaseHandlerPICKLE import databaseHandlerPICKLE
	#from PVS_DatabaseHandlerPICKLE import databaseHandlerPICKLE
	printl("PVS_DatabaseHandlerPICKLE Loaded :)", None, "W")
except Exception, ex:
	printl("Exception: PVS_DatabaseHandlerPICKLE not Loaded :(   "+ str(ex), None, "W")
		
try:
	from Plugins.Extensions.ProjectValerieSync.PVS_DatabaseHandlerTXD import databaseHandlerTXD
	#from PVS_DatabaseHandlerTXD import databaseHandlerTXD
	printl("PVS_DatabaseHandlerTXD Loaded    :)", None, "W")
except Exception, ex:
	printl("Exception: PVS_DatabaseHandlerTXD not Loaded :(   "+ str(ex), None, "W")

#------------------------------------------------------------------------------------------

gDatabase = None
gDatabaseMutex = Lock()

class Database(object):
	DB_PATH           = config.plugins.pvmc.configfolderpath.value
	DB_PATH_EPISODES  = config.plugins.pvmc.configfolderpath.value + "episodes/"

	FAILEDDB = DB_PATH + "failed.db"
	MOVIESDB   = DB_PATH + "movies.db"
	TVSHOWSDB  = DB_PATH + "tvshows.db"
	EPISODESDB = DB_PATH + "episodes.db"

	MOVIESTXD  = DB_PATH + "movies.txd"
	TVSHOWSTXD = DB_PATH + "tvshows.txd"
	
	DB_NONE = 0
	DB_TXD = 2
	DB_PICKLE = 3
	DB_SQLITE= 4

	if DB_SQLITE_LOADED and os.path.exists(DB_PATH + "usesql"):
		USE_DB_TYPE    	= DB_SQLITE
	else:
		USE_DB_TYPE    	= DB_PICKLE
		
	#USE_DB_TYPE    	= DB_TXD
	USE_BACKUP_TYPE = DB_NONE  	# To do: will always backup to DB_PICKLE ????
					#   	 
	
	TXD_VERSION = 3
	
	def __init__(self):
		printl("", self)
			
		if self.USE_DB_TYPE == self.DB_SQLITE:			
			self.dbHandler = databaseHandlerSQL().getInstance("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
			if self.dbHandler.DB_SQLITE_FIRSTTIME:
				printl("Sql FirstTime", self)					 
				self.importDataToSql()
				self.dbHandler.DB_SQLITE_FIRSTTIME = False

					
		if self.USE_DB_TYPE == self.DB_PICKLE:			
			self.dbHandler = databaseHandlerPICKLE().getInstance()
		
		if self.USE_DB_TYPE == self.DB_TXD:
			self.dbHandler = databaseHandlerTXD().getInstance()
		
		# Deactivate usage of txd files
		#if os.path.exists(self.DB_PATH + self.DB_TXD_FILENAME_M):
		#	self.setDBType(self.DB_TXD)
		#
		#elif os.path.exists(self.DB_PATH + self.DB_TXT_FILENAME_M):
		#	self.setDBType(self.DB_TXT)
			#self.setDBVersion(DB_TXD)
		# No exception if exists movies.txd and no tvshows.txd

	def importDataToSql (self):
		printl("->", self)
		printl("Importing Data", self)
		self.dbHandler = databaseHandlerPICKLE().getInstance()
		self.reload()	# Load from PICKLE
		self.dbHandler = databaseHandlerSQL().getInstance("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
		self.save()  	# save to Database SQL
		try:
			pass #os.rename(self.DB_TXD, self.DB_TXD +'.'+ str(time.time()) + '.bak')
		except Exception, ex:
			printl("Backup movie txd failed! Ex: " + str(ex), __name__, "E")

	def setDBType(self, version):
		self.USE_DB_TYPE = version
		printl("DB Type set to " + str(version), self)

	def getDBTypeText(self):
		if self.USE_DB_TYPE == self.DB_TXD:
			return "TXD"
		elif self.USE_DB_TYPE == self.DB_PICKLE:
			return "Pickle"
		elif self.USE_DB_TYPE == self.DB_SQLITE:
			return "SQLite"
		else:
			return "No DB Type defined"

	def getInstance(self):
		printl("", self, "D")
		global gDatabase
		global gDatabaseMutex
		
		#printl("Acquiring Mutex", self, "D")
		gDatabaseMutex.acquire()
		#printl("Acquired Mutex", self, "D")
		
		if gDatabase is None:
			printl("Creating new Database instance", self)
			self.reload()
			gDatabase = self
		
		#printl("Releasing Mutex", self, "D")
		gDatabaseMutex.release()
		#printl("Released Mutex", self, "D")
		
		return gDatabase

	def reload(self):
		printl("", self, "D")
		self.dbMovies = {}
		self.dbSeries = {}
		self.dbEpisodes = {}
		
		self.dbFailed = []
		
		self.duplicateDetector = []
		
		self._load()

	def transformGenres(self):
		for key in self.dbMovies:
			transformedGenre = ""
			for genre in self.dbMovies[key].Genres.split("|"):
				if Genres.isGenre(genre) is False:
					newGenre = Genres.getGenre(genre)
					if newGenre != "Unknown":
						printl("GENRE: " + str(genre) + " -> " + str(newGenre), self)
						transformedGenre += newGenre + u"|"
				else:
					transformedGenre += genre + u"|"
			if len(transformedGenre) > 0:
				transformedGenre = transformedGenre[:len(transformedGenre) - 1] # Remove the last pipe
			self.dbMovies[key].Genres = transformedGenre
		
		for key in self.dbSeries:
			transformedGenre = ""
			for genre in self.dbSeries[key].Genres.split("|"):
				if Genres.isGenre(genre) is False:
					newGenre = Genres.getGenre(genre)
					if newGenre != "Unknown":
						printl("GENRE: " + str(genre) + " -> " + str(newGenre), self)
						transformedGenre += newGenre + u"|"
				else:
					transformedGenre += genre + u"|"
			if len(transformedGenre) > 0:
				transformedGenre = transformedGenre[:len(transformedGenre) - 1] # Remove the last pipe
			self.dbSeries[key].Genres = transformedGenre
			
			if key in self.dbEpisodes:
				for season in self.dbEpisodes[key]:
					for episode in self.dbEpisodes[key][season]:
						transformedGenre = ""
						for genre in self.dbEpisodes[key][season][episode].Genres.split("|"):
							if Genres.isGenre(genre) is False:
								newGenre = Genres.getGenre(genre)
								if newGenre != "Unknown":
									printl("GENRE: " + str(genre) + " -> " + str(newGenre), self)
									transformedGenre += newGenre + u"|"
							else:
								transformedGenre += genre + u"|"
						if len(transformedGenre) > 0:
							transformedGenre = transformedGenre[:len(transformedGenre) - 1] # Remove the last pipe
						self.dbEpisodes[key][season][episode].Genres = transformedGenre

	def clearFailed(self):
		try:
			del self.dbFailed[:]
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def addFailed(self, entry):
		self.dbFailed.append(entry)

	def removeFailed(self, entry):
		if entry in self.dbFailed:
			self.dbFailed.remove(entry)

	def deleteMissingFiles(self):
		listMissing = []
		
		for key in self.dbMovies:
			m = self.dbMovies[key]
			path = m.Path + u"/" + m.Filename + u"." + m.Extension
			if os.path.exists(Utf8.utf8ToLatin(path)) is False:
				listMissing.append(m)
		
		for key in self.dbSeries:
			if key in self.dbEpisodes:
				for season in self.dbEpisodes[key]:
					for episode in self.dbEpisodes[key][season]:
						m = self.dbEpisodes[key][season][episode]
						path = m.Path + u"/" + m.Filename + u"." + m.Extension
						if os.path.exists(Utf8.utf8ToLatin(path)) is False:
							listMissing.append(m)
		
		printl("Missing: " + str(len(listMissing)), self)
		for m in listMissing:
			self.remove(m)

	def searchDeleted(self):
		for key in self.dbMovies:
			m = self.dbMovies[key]
			path = m.Path + u"/" + m.Filename + u"." + m.Extension
			if os.path.exists(Utf8.utf8ToLatin(path)) is False:
				printl(":-( " + Utf8.utf8ToLatin(path), self)
		
		for key in self.dbSeries:
			if key in self.dbEpisodes:
				for season in self.dbEpisodes[key]:
					for episode in self.dbEpisodes[key][season]:
						m = self.dbEpisodes[key][season][episode]
						path = m.Path + u"/" + m.Filename + u"." + m.Extension
						if os.path.exists(Utf8.utf8ToLatin(path)) is False:
							printl(":-( " + Utf8.utf8ToLatin(path), self)

	##
	# Checks if file is already in the db
	# @param path: utf-8 
	# @param filename: utf-8 
	# @param extension: utf-8 
	# @return: True if already in db, False if not
	def checkDuplicate(self, path, filename, extension):
		for key in self.dbMovies:
			if self.dbMovies[key].Path == path:
				if self.dbMovies[key].Filename == filename:
					if self.dbMovies[key].Extension == extension:
						return self.dbMovies[key]
		
		for key in self.dbSeries:
			if key in self.dbEpisodes:
				for season in self.dbEpisodes[key]:
					for episode in self.dbEpisodes[key][season]:
						if self.dbEpisodes[key][season][episode].Path == path:
							if self.dbEpisodes[key][season][episode].Filename == filename:
								if self.dbEpisodes[key][season][episode].Extension == extension:
									return self.dbEpisodes[key][season][episode]
		
		return None

	def remove(self, media, isMovie=False, isSerie=False, isEpisode=False):
		printl("isMovie=" + str(media.isMovie) + " isSerie=" + str(media.isSerie) + " isEpisode=" + str(media.isEpisode), self)
		if media.isMovie or isMovie:
			movieKey = media.ImdbId
			#movieKey = media.Id			
			if self.dbMovies.has_key(movieKey) is True:
				del(self.dbMovies[movieKey])	
				return True
		if media.isSerie or isSerie:
			serieKey = media.TheTvDbId
			#serieKey = media.Id
			if self.dbSeries.has_key(serieKey) is True:
				del(self.dbSeries[serieKey])
				return True
		if media.isEpisode or isEpisode:
			serieKey   = media.TheTvDbId
			#serieKey   = media.Id
			#seasonKey  = media.Season
			#episodeKey = media.Episode
			if self.dbEpisodes.has_key(serieKey) is True:
				if self.dbEpisodes[serieKey].has_key(media.Season) is True:
					if self.dbEpisodes[serieKey][c].has_key(media.Episode) is True:
						del(self.dbEpisodes[serieKey][media.Season][media.Episode])
						if len(self.dbEpisodes[serieKey][media.Season]) == 0:
							del(self.dbEpisodes[serieKey][media.Season])
						if len(self.dbEpisodes[serieKey]) == 0:
							del(self.dbEpisodes[serieKey])
							if self.dbSeries.has_key(serieKey) is True:
								del(self.dbSeries[serieKey])
						return True
		return False

	_addFailedCauseOf = None

	def getAddFailedCauseOf(self):
		cause = self._addFailedCauseOf
		self._addFailedCauseOf = None
		return cause.Path + u"/" + cause.Filename + u"." + cause.Extension

	##
	# Adds media files to the db
	# @param media: The media file
	# @return: False if file is already in db or movie already in db, else True 
	def add(self, media):
		# Checks if a tvshow is already in the db, if so then we dont have to readd it a second time
		if media.isSerie:
			serieKey = media.TheTvDbId
			#serieKey = media.Id
			if self.dbSeries.has_key(serieKey) is False:
				self.dbSeries[serieKey] = media
				return True
			else:
				#self._addFailedCauseOf = self.dbSeries[media.TheTvDbId]
				#return False
				return True # We return true here cause this is not a failure but simply means that the tvshow already exists in the db
		
		media.Path = media.Path.replace("\\", "/")
		# Checks if the file is already in db
		if self.checkDuplicate(media.Path, media.Filename, media.Extension):
			# This should never happen, this means that the same file is already in the db
			# But is a failure describtion here necessary ?
			return False
		
		pth = media.Path + "/" + media.Filename + "." + media.Extension
		self.duplicateDetector.append(pth)
		
		if media.isMovie:
			movieKey = media.ImdbId
			#movieKey = media.Id
			if self.dbMovies.has_key(movieKey) is False:
				self.dbMovies[movieKey] = media
			else: 
				self._addFailedCauseOf = self.dbMovies[movieKey]
				return False
		elif media.isEpisode:
			serieKey = media.TheTvDbId
			#serieKey = media.Id
			if self.dbEpisodes.has_key(serieKey) is False:
				self.dbEpisodes[serieKey] = {}
			
			if self.dbEpisodes[serieKey].has_key(media.Season) is False:
				self.dbEpisodes[serieKey][media.Season] = {}
			
			if self.dbEpisodes[serieKey][media.Season].has_key(media.Episode) is False:
				self.dbEpisodes[serieKey][media.Season][media.Episode] = media
			else:
				self._addFailedCauseOf = self.dbEpisodes[serieKey][media.Season][media.Episode]
				return False
		return True

	def __str__(self):
		epcount = 0
		for key in self.dbSeries:
			if key in self.dbEpisodes:
				for season in self.dbEpisodes[key]:
					epcount +=  len(self.dbEpisodes[key][season])
		rtv = unicode(len(self.dbMovies)) + \
				u" " + \
				unicode(len(self.dbSeries)) + \
				u" " + \
				unicode(epcount)
		return Utf8.utf8ToLatin(rtv)


	def save(self):
		global gDatabaseMutex
		gDatabaseMutex.acquire()
		# Always safe pickel as this increses fastsync a lot
		
		# will be the backup
		#self.savePickel() 
		
		self.dbHandler.saveMovies(self.dbMovies)
		self.dbHandler.saveSeries(self.dbSeries)
		self.dbHandler.saveEpisodes(self.dbEpisodes)
		self.dbHandler.saveFailed(self.dbFailed)
		
		#if self.USE_DB_TYPE == self.DB_TXD:
		#	self.saveTxd()
		#elif self.USE_DB_TYPE == self.DB_SQLITE:
		#	self.saveSql()
		gDatabaseMutex.release()

	def _load(self):
		if len(self.dbFailed) == 0:# and os.path.isfile(self.FAILEDDB):
			self.dbFailed = self.dbHandler.getFailedFiles()
		
		if len(self.dbMovies) == 0:
			self.dbMovies = self.dbHandler.getAllMovies()			
		
		if len(self.dbSeries) == 0 or len(self.dbEpisodes) == 0:
			self.dbSeries = self.dbHandler.getAllSeries()
			if self.USE_DB_TYPE == self.DB_TXD:
				self.dbEpisodes = self.dbHandler.getEpisodesFromAllSeries(self.dbSeries)
			else:
				self.dbEpisodes = self.dbHandler.getAllEpisodes()
					
		# FIX: GHOSTFILES
		if self.dbEpisodes.has_key("0"):
			ghost = self.dbEpisodes["0"].values()
			for season in ghost:
				for episode in season.values():
					self.remove(episode)
			if self.dbEpisodes.has_key("0"):
				del self.dbEpisodes["0"]
		
		for tvshow in self.dbEpisodes.values():
			for season in tvshow.values():
				for episode in season.values():
					if episode.isEpisode is False:
						b = self.remove(episode, isEpisode=True)
						printl("RM: " + str(b), self)
						