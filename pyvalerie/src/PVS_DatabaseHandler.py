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
#   v0.Initial - Zuki - renamed from database.py
#
#   v1 15/07/2011 - Zuki - minor changes to support SQL DB
#			 - Separate LoadALL in 3 processes (movies,series,failed)
#			 - Added Database requests to 
#   v2 18/07/2011 - Zuki - Added Counters for Movies/Series
#   v3 21/07/2011 - Zuki - Added new functions to access Series/Episodes 
##
################################################################################
# Function			Parameters		Return
################################################################################
# moviesGetAll						dict of MediaInfo
# moviesGetAllValues					list of MediaInfo 
# moviesGetWithKey		movieKey		MediaInfo
# moviesGetPkWithImdb		ImdbID			ID
# moviesCount						Count
#
# seriesGetAll						dict of MediaInfo
# seriesGetAllValues					list of MediaInfo
# seriesGetWithKey		serieKey		MediaInfo
# seriesGetPkWithTheTvDb	theTvDbId		ID
# seriesGetSeasons		serieKey		dict of MediaInfo
# seriesGetEpisodes		serieKey=None		list of MediaInfo
#				season=None
# seriesGetEpisode		serieKey,season,episode	MediaInfo
# seriesCount						Count
# seriesCountSeasons		serieKey		Count
# seriesCountEpisodes		serieKey,season		Count
#
# seriesDeleteCascadeOfSerie	serieKey		Boolean
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
from Plugins.Extensions.ProjectValerie.__common__ import log as log
	
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
	DB_NONE = 0
	DB_TXD = 2
	DB_PICKLE = 3
	DB_SQLITE= 4

	DB_PATH           = config.plugins.pvmc.configfolderpath.value

	if DB_SQLITE_LOADED and os.path.exists(DB_PATH + "usesql"):
		USE_DB_TYPE    	= DB_SQLITE
	else:
		USE_DB_TYPE    	= DB_PICKLE
		
	USE_BACKUP_TYPE = DB_NONE  	# To do: will always backup to DB_PICKLE ????
	
	USE_INDEXES = False  # Create indexes key/id
	PRELOADDB   = True   # Reload All tables on Start (default)
	
	CONFIGKEY  = -999999
	
	_dbMovies = {}
	_dbSeries = {}
	_dbEpisodes = {}
		
	dbFailed = []		
	
	def __init__(self):
		log("->", self, 10)
			
		if self.USE_DB_TYPE == self.DB_SQLITE:			
			self.dbHandler = databaseHandlerSQL().getInstance("from __init__")
			if self.dbHandler.DB_SQLITE_FIRSTTIME:
				printl("Sql FirstTime", self)					 
				self.importDataToSql()#.addCallback(self.ImportDone).addErrback(self.ImportError)

				self.dbHandler.DB_SQLITE_FIRSTTIME = False
					
		if self.USE_DB_TYPE == self.DB_PICKLE:			
			self.dbHandler = databaseHandlerPICKLE().getInstance()
		
		if self.USE_DB_TYPE == self.DB_TXD:
			self.dbHandler = databaseHandlerTXD().getInstance()
	
	def importDataToSql (self):
		log("->", self, 10)
		try:
			printl("Importing Data", self)
			self.dbHandler = databaseHandlerPICKLE().getInstance()
			self.reload()	# Load from PICKLE
			self.dbHandler = databaseHandlerSQL().getInstance("ImportDataToSql")
			printl("5555555555555555", self)
			self.save()  	# save to Database SQL
			try:
				pass #os.rename(self.DB_TXD, self.DB_TXD +'.'+ str(time.time()) + '.bak')
			except Exception, ex:
				printl("Backup movie txd failed! Ex: " + str(ex), __name__, "E")
		except Exception, ex:
			printl("Failed Import to SQL! Reloading Pickles Ex: " + str(ex), __name__, "E")
			self.dbHandler = databaseHandlerPICKLE().getInstance()
			self.reload()	# Load from PICKLE
			

	def setDBType(self, version):
		self.USE_DB_TYPE = version
		log("DB Type set to " + str(version), self)

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
		log("->", self, 10)
		global gDatabase
		global gDatabaseMutex
		
		if gDatabase is None:
			printl("Acquiring Mutex", self, "W")
			gDatabaseMutex.acquire()
			try:
				printl("Creating new Database instance", self)
				#self.reload()
				if self.PRELOADDB:
					self.reload()  # RELOAD ALLL ?????
				else:
					self.clearMemory()
					self._dbMovies = None
					
				gDatabase = self
			finally:	
				gDatabaseMutex.release()
				printl("Released Mutex", self, "W")
		
		return gDatabase

	def clearMemory(self):
		log("->", self, 10)
		self._dbMovies = {}
		self._dbSeries = {}
		self._dbEpisodes = {}
		self.dbFailed2 = {}
		
		self.dbFailed = []
		
		self.duplicateDetector = []
		
		self.idxMoviesByImdb = {}
		self.idxSeriesByTheTvDb = {}

	def reload(self):
		log("->", self, 10)
		self.clearMemory()
		
		#self._load()
		self.loadMoviesFromDB()
		self.loadSeriesEpisodesFromDB()
		self.loadFailed()

	def transformGenres(self):
		for key in self.moviesGetAll():
			transformedGenre = ""
			for genre in self._dbMovies[key].Genres.split("|"):
				if Genres.isGenre(genre) is False:
					newGenre = Genres.getGenre(genre)
					if newGenre != "Unknown":
						printl("GENRE: " + str(genre) + " -> " + str(newGenre), self)
						transformedGenre += newGenre + u"|"
				else:
					transformedGenre += genre + u"|"
			if len(transformedGenre) > 0:
				transformedGenre = transformedGenre[:len(transformedGenre) - 1] # Remove the last pipe
			self._dbMovies[key].Genres = transformedGenre
		
		for key in self.seriesGetAll():
			transformedGenre = ""
			for genre in self._dbSeries[key].Genres.split("|"):
				if Genres.isGenre(genre) is False:
					newGenre = Genres.getGenre(genre)
					if newGenre != "Unknown":
						printl("GENRE: " + str(genre) + " -> " + str(newGenre), self)
						transformedGenre += newGenre + u"|"
				else:
					transformedGenre += genre + u"|"
			if len(transformedGenre) > 0:
				transformedGenre = transformedGenre[:len(transformedGenre) - 1] # Remove the last pipe
			self._dbSeries[key].Genres = transformedGenre
			
			if key in self._dbEpisodes:
				for season in self._dbEpisodes[key]:
					for episode in self._dbEpisodes[key][season]:
						transformedGenre = ""
						for genre in self._dbEpisodes[key][season][episode].Genres.split("|"):
							if Genres.isGenre(genre) is False:
								newGenre = Genres.getGenre(genre)
								if newGenre != "Unknown":
									printl("GENRE: " + str(genre) + " -> " + str(newGenre), self)
									transformedGenre += newGenre + u"|"
							else:
								transformedGenre += genre + u"|"
						if len(transformedGenre) > 0:
							transformedGenre = transformedGenre[:len(transformedGenre) - 1] # Remove the last pipe
						self._dbEpisodes[key][season][episode].Genres = transformedGenre

	def clearFailed(self):
		try:
			del self.dbFailed[:]
		except Exception, ex:
			log("Exception: " + str(ex), self, 2)

	def addFailed(self, entry):
		self.dbFailed.append(entry)

	def removeFailed(self, entry):
		if entry in self.dbFailed:
			self.dbFailed.remove(entry)

	def deleteMissingFiles(self):
		listMissing = []
		
		for key in self.moviesGetAll():
			m = self._dbMovies[key]
			path = m.Path + u"/" + m.Filename + u"." + m.Extension
			if os.path.exists(Utf8.utf8ToLatin(path)) is False:
				listMissing.append(m)
		
		for key in self.seriesGetAll():
			if key in self._dbEpisodes:
				for season in self._dbEpisodes[key]:
					for episode in self._dbEpisodes[key][season]:
						m = self._dbEpisodes[key][season][episode]
						path = m.Path + u"/" + m.Filename + u"." + m.Extension
						if os.path.exists(Utf8.utf8ToLatin(path)) is False:
							listMissing.append(m)
		
		printl("Missing: " + str(len(listMissing)), self)
		for m in listMissing:
			self.remove(m)

	def searchDeleted(self):
		for key in self.moviesGetAll():
			m = self._dbMovies[key]
			path = m.Path + u"/" + m.Filename + u"." + m.Extension
			if os.path.exists(Utf8.utf8ToLatin(path)) is False:
				printl(":-( " + Utf8.utf8ToLatin(path), self)
		
		for key in self.seriesGetAll():
			if key in self._dbEpisodes:
				for season in self._dbEpisodes[key]:
					for episode in self._dbEpisodes[key][season]:
						m = self._dbEpisodes[key][season][episode]
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
		for key in self.moviesGetAll():
			if self._dbMovies[key].Path == path:
				if self._dbMovies[key].Filename == filename:
					if self._dbMovies[key].Extension == extension:
						return self._dbMovies[key]
		
		for key in self.seriesGetAll():
			if key in self._dbEpisodes:
				for season in self._dbEpisodes[key]:
					for episode in self._dbEpisodes[key][season]:
						if self._dbEpisodes[key][season][episode].Path == path:
							if self._dbEpisodes[key][season][episode].Filename == filename:
								if self._dbEpisodes[key][season][episode].Extension == extension:
									return self._dbEpisodes[key][season][episode]
		
		return None

	def remove(self, media, is_Movie=False, is_Serie=False, is_Episode=False):
		printl("is Movie=" + str(media.isTypeMovie()) + " is Serie=" + str(media.isTypeSerie()) + " is Episode=" + str(media.isTypeEpisode()), self)
		if media.isTypeMovie() or is_Movie:
			movieKey = media.ImdbId
			#movieKey = media.Id			
			if self._dbMovies.has_key(movieKey) is True:
				del(self._dbMovies[movieKey])	
				return True
		if media.isTypeSerie() or is_Serie:
			serieKey = media.TheTvDbId
			#serieKey = media.Id
			if self._dbSeries.has_key(serieKey) is True:
				del(self._dbSeries[serieKey])
				return True
		if media.isTypeEpisode() or is_Episode:
			serieKey   = media.TheTvDbId
			#serieKey   = media.Id
			#seasonKey  = media.Season
			#episodeKey = media.Episode
			if self._dbEpisodes.has_key(serieKey) is True:
				if self._dbEpisodes[serieKey].has_key(media.Season) is True:
					if self._dbEpisodes[serieKey][media.Season].has_key(media.Episode) is True:
						del(self._dbEpisodes[serieKey][media.Season][media.Episode])
						if len(self._dbEpisodes[serieKey][media.Season]) == 0:
							del(self._dbEpisodes[serieKey][media.Season])
						if len(self._dbEpisodes[serieKey]) == 0:
							del(self._dbEpisodes[serieKey])
							if self._dbSeries.has_key(serieKey) is True:
								del(self._dbSeries[serieKey])
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

		if media.MediaType == MediaInfo.FAILEDSYNC:
			nextID = len(self.dbFailed2)
			self.dbFailed2[nextID] = media			

		# Checks if a tvshow is already in the db, if so then we dont have to readd it a second time
		if media.isTypeSerie():
			serieKey = media.TheTvDbId
			#serieKey = media.Id
			#if USE_INDEXES:
			#	if self.idxSeriesByThetvdb.has_key(media.TheTvDbId) is None:
				
			#else:
			
			if self._dbSeries.has_key(serieKey) is False:
				self._dbSeries[serieKey] = media
				return True
			else:
				#self._addFailedCauseOf = self._dbSeries[media.TheTvDbId]
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
		
		if media.isTypeMovie():
			movieKey = media.ImdbId
			#movieKey = media.Id
			if self._dbMovies.has_key(movieKey) is False:
				self._dbMovies[movieKey] = media
			else: 
				self._addFailedCauseOf = self._dbMovies[movieKey]
				return False
		elif media.isTypeEpisode():
			serieKey = media.TheTvDbId
			#printl("serie: "+serieKey+ " season: " + str(media.Season) + " Episode: "+str(media.Episode))
			#serieKey = media.Id
			if self._dbEpisodes.has_key(serieKey) is False:
				self._dbEpisodes[serieKey] = {}
			
			if self._dbEpisodes[serieKey].has_key(media.Season) is False:
				self._dbEpisodes[serieKey][media.Season] = {}
			
			if self._dbEpisodes[serieKey][media.Season].has_key(media.Episode) is False:
				self._dbEpisodes[serieKey][media.Season][media.Episode] = media
			else:
				self._addFailedCauseOf = self._dbEpisodes[serieKey][media.Season][media.Episode]
				return False
		return True

	def __str__(self):
		epcount = 0
		for key in self.seriesGetAll():
			if key in self._dbEpisodes:
				for season in self._dbEpisodes[key]:
					epcount +=  len(self._dbEpisodes[key][season])
		rtv = unicode(len(self._dbMovies)) + \
				u" " + \
				unicode(len(self._dbSeries)) + \
				u" " + \
				unicode(epcount)
		return Utf8.utf8ToLatin(rtv)


	def save(self):
		log("->", self, 10)
		global gDatabaseMutex
		printl("Acquiring Mutex", self, "W")
		gDatabaseMutex.acquire()
		try:
			printl("Acquired Mutex", self, "W")
			# Always safe pickel as this increses fastsync a lot
			
			# will be the backup
			#self.savePickel() 
			
			self.dbHandler.saveMovies(self._dbMovies)
			self.dbHandler.saveSeries(self._dbSeries)
			self.dbHandler.saveEpisodes(self._dbEpisodes)
			self.dbHandler.saveFailed(self.dbFailed)
			#self.dbHandler.saveFailed2(self.dbFailed2)
			return True
		except Exception, ex:
			printl("Failed Save! Ex: " + str(ex), __name__, "E")
			return False
		finally:	
			gDatabaseMutex.release()
			printl("Released Mutex", self, "W")
		
	def loadMoviesFromDB(self):
		log("->", self, 10)
		start_time = time.time()
		if len(self._dbMovies) == 0:
			self._dbMovies = self.dbHandler.getAllMovies()			
			if self.USE_INDEXES:
				self.createMoviesIndexes()
				
		elapsed_time = time.time() - start_time
		log("LoadMovies Took : " + str(elapsed_time), self, 11)

	def loadSeriesEpisodesFromDB(self):
		log("->", self, 10)
		start_time = time.time()
		if len(self._dbSeries) == 0 or len(self._dbEpisodes) == 0:
			self._dbSeries = self.dbHandler.getAllSeries()
			if self.USE_DB_TYPE == self.DB_TXD:
				self._dbEpisodes = self.dbHandler.getEpisodesFromAllSeries(self._dbSeries)
			else:
				self._dbEpisodes = self.dbHandler.getAllEpisodes()
			if self.USE_INDEXES:
				self.createSeriesIndexes()
					
		# FIX: GHOSTFILES
		if self._dbEpisodes.has_key("0"):
			ghost = self._dbEpisodes["0"].values()
			for season in ghost:
				for episode in season.values():
					self.remove(episode)
			if self._dbEpisodes.has_key("0"):
				del self._dbEpisodes["0"]
		
		#for tvshow in self._dbEpisodes.values():
		#	for season in tvshow.values():
		#		for episode in season.values():
		#			if not episode.isTypeEpisode():
		#				b = self.remove(episode, isEpisode=True)
		#				printl("RM: " + str(b), self)
		for serie in self._dbEpisodes:
			if serie != self.CONFIGKEY: #not ConfigRecord
				for seasonKey in self._dbEpisodes[serie]:
					season = self._dbEpisodes[serie][seasonKey]
					for episodeKey in season:
						episode = season[episodeKey]
						if type(episode) is MediaInfo:
							if not episode.isTypeEpisode():
								b = self.remove(episode, isEpisode=True)
								printl("RM: " + str(b), self)
				
		elapsed_time = time.time() - start_time
		printl("Load Series/Episodes Took : " + str(elapsed_time), self)

	def loadFailed(self):
		if len(self.dbFailed) == 0:
			self.dbFailed = self.dbHandler.getFailedFiles()
		#self.dbFailed2

#
#################################   MOVIES   ################################# 
#
	#not tested
	def createMoviesIndexes(self):
		log("->", self, 10)
		start_time = time.time()
		self.idxMoviesByImdb = {}
		for key in self._dbMovies:
			if key != self.CONFIGKEY:		# only for Pickle
				self.idxMoviesByImdb[self._dbMovies[key].ImdbId] = key
		elapsed_time = time.time() - start_time
		log("Indexing Took : " + str(elapsed_time), self, 11)
	
	#Call when data is needed, to verify if is loaded
	def _moviesCheckLoaded(self):
		#log("->", self, 10)
		if self._dbMovies is None:
			self.loadMoviesFromDB()

	def moviesGetAll(self):
		log("->", self, 15)
		self._moviesCheckLoaded()
		newList	= self._dbMovies.copy()
		if self.CONFIGKEY in newList:		# only for Pickle
			del newList[self.CONFIGKEY]
		return newList

	def moviesGetAllValues(self):
		log("->", self, 15)
		return self.moviesGetAll().values()

	def moviesGetWithKey(self, movieKey):
		log("->", self, 15)
		self._moviesCheckLoaded()
		start_time = time.time()
		element = None
		if movieKey in self._dbMovies:
			element = self._dbMovies[movieKey]
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return element

	def moviesGetPkWithImdb(self, imdbId):
		log("->", self, 15)
		self._moviesCheckLoaded()
		start_time = time.time()
		key = None
		if self.USE_INDEXES:
			# use Indexes loaded at beginning
			# indexing 0.0007		
			#key = self.idxMoviesImdb[imdb]
			#element = self._dbMovies[key]			
			pass
		else:			
			# without indexing 0.02
			for movieKey in self.db._dbMovies:
				if movieKey != self.CONFIGKEY:		# only for Pickle
					if self._dbMovies[movieKey].ImdbId == imdbId:
						key = movieKey
						break
		
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return key

	def moviesCount(self):
		log("->", self, 20)
		return len(self.moviesGetAll())
		
	
#	
#################################   SERIES   ################################# 
#
	#not tested
	def createSeriesIndexes(self):
		log("->", self, 10)
		start_time = time.time()
		self.idxSeriesByTheTvDb = {}
		for key in self._dbSeries:
			self.idxSeriesByTheTvDb[self._dbSeries[key].TheTvDbId] = key
		elapsed_time = time.time() - start_time
		printl("Indexing Took : " + str(elapsed_time), self)

	#Call when data is needed, to verify if is loaded
	def _seriesCheckLoaded(self):
		log("->", self, 15)
		if self._dbSeries is None:
			self.loadSeriesEpisodesFromDB()

	def seriesGetAll(self):
		log("->", self, 15)
		self._seriesCheckLoaded()
		newList	= self._dbSeries.copy()
		if self.CONFIGKEY in newList:
			del newList[self.CONFIGKEY]
		return newList

	def seriesGetAllValues(self):
		log("->", self, 15)
		return self.seriesGetAll().values()
		
	def seriesGetWithKey(self, key):
		log("->", self, 15)
		self._seriesCheckLoaded()
		start_time = time.time()
		element = None
		if key in self._dbSeries:
			element = self._dbSeries[key]
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return element
	
	def seriesGetPkWithTheTvDbId(self, inTheTvDbId):
		log("->", self, 15)
		self._seriesCheckLoaded()
		start_time = time.time()
		key = None
		if self.USE_INDEXES:
			# use Indexes loaded at beginning
			# indexing 0.0007		
			#serieKey = self.idxSeriesTheTvDb[thetvdb]
			pass
		else:			
			# without indexing 0.02s
			for serieKey in self._dbSeries:
				if serieKey != self.CONFIGKEY:		# only for Pickle
					if self._dbSeries[serieKey].TheTvDbId == inTheTvDbId:
						key = serieKey
						break
		
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return key

	#def seriesGetAllEpisodes(self):
	#	log("->", self, 15)
	#	self._seriesCheckLoaded()
	#	list = []
	#	for serieKey in self._dbEpisodes:
	#		if serieKey != self.CONFIGKEY:
	#			for season in self._dbEpisodes[serieKey]:
	#				list += self._dbEpisodes[serieKey][season].values()
	#	return list	
	#def seriesGetEpisodesOfSerie(self, serieKey):
	#	log("->", self, 15)
	#	self._seriesCheckLoaded()
	#	list = []
	#	if serieKey in self._dbEpisodes:
	#		for season in self._dbEpisodes[serieKey]:
	#			list += self._dbEpisodes[serieKey][season].values()
	#	return list
	#
	#def seriesGetEpisodesOfSeason(self, serieKey, season):
	#	log("->", self, 15)
	#	self._seriesCheckLoaded()
	#	if serieKey in self._dbEpisodes:
	#		if season in self._dbEpisodes[serieKey]:
	#			return self._dbEpisodes[serieKey][season].values()

	def seriesGetEpisodes(self, serieKey=None, season=None):
		log("->", self, 15)
		self._seriesCheckLoaded()
		if serieKey is None:		# seriesGetAllEpisodes
			list = []
			for serieKey in self._dbEpisodes:
				if serieKey != self.CONFIGKEY:
					for season in self._dbEpisodes[serieKey]:
						list += self._dbEpisodes[serieKey][season].values()
			return list
		elif season is None:		# seriesGetEpisodesOfSerie
			list = []
			if serieKey in self._dbEpisodes:
				for season in self._dbEpisodes[serieKey]:
					list += self._dbEpisodes[serieKey][season].values()				
			return list
		else:				# seriesGetEpisodesOfSeason
			if serieKey in self._dbEpisodes:
				if season in self._dbEpisodes[serieKey]:
					return self._dbEpisodes[serieKey][season].values()
		
		return None
	
	def seriesGetEpisode(self, serieKey, season, episode):
		log("->", self, 15)
		self._seriesCheckLoaded()
		element = None
		if serieKey in self._dbEpisodes:
			if season in self._dbEpisodes[serieKey]:
				if episode in self._dbEpisodes[serieKey][season]:
					element = self._dbEpisodes[serieKey][season][episode]
		return element
		
	def seriesGetSeasons(self, serieKey):
		log("->", self, 15)
		self._seriesCheckLoaded()
		if serieKey in self._dbEpisodes:
			return self._dbEpisodes[serieKey].keys()
				
		return self.seriesGetAll().values()
				
	
	def seriesCount(self):
		log("->", self, 10)
		return len(self.seriesGetAll())

	def seriesCountSeasons(self, serieKey):
		log("->", self, 15)
		self._seriesCheckLoaded()
		count = None
		if serieKey in self._dbEpisodes:
			count = len(self._dbEpisodes[serieKey])
		return count
	
	def seriesCountEpisodes(self, serieKey=None, season=None):
		log("->", self, 15)
		self._seriesCheckLoaded()
		count = 0
		if serieKey is None:		# seriesCountAllEpisodes
			for serieKey in self._dbEpisodes:
				if serieKey != self.CONFIGKEY:
					for season in self._dbEpisodes[serieKey]:
						count += len(self._dbEpisodes[serieKey][season])
		elif season is None:		# 
			if serieKey in self._dbEpisodes:
				for season in self._dbEpisodes[serieKey]:
					count += len(self._dbEpisodes[serieKey][season])
		else:
			if serieKey in self._dbEpisodes:
				if season in self._dbEpisodes[serieKey]:
					count = len(self._dbEpisodes[serieKey][season])
		
		return count
	
	#not tested
	def seriesDeleteCascadeOfSerie(self, serieKey):
		log("->", self, 10)
		self._seriesCheckLoaded()
		if serieKey in self._dbEpisodes:
			del(self._dbEpisodes[serieKey])
		if serieKey in self._dbSeries:	
			del(self._dbSeries[serieKey])
		return True





	#getCountOfSeasons("thetvdbid")
	#getCountOfEpisodesOfSeason("thetvdbid", "season")
	#deleteTvShowWithCorrespondingEpisodes();

	#def createSeriesIndexes(self):
	#	start_time = time.time()
	#	for key in self._dbSeries:
	#		self.idxSeriesByThetvdb[self._dbSeries[key].TheTvDbId] = key
	#	elapsed_time = time.time() - start_time
	#	printl("Indexing Took : " + str(elapsed_time), self)
