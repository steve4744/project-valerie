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
# getMovies						dict of MediaInfo
# getMoviesValues					list of MediaInfo 
# getMoviesWithKey		movieKey		MediaInfo
# getMoviesPkWithImdb		ImdbID			ID
# getMoviesCount					Count
#
# getSeries						dict of MediaInfo
# getSeriesValues					list of MediaInfo
# getSeriesWithKey		serieKey		MediaInfo
# getSeriesPkWithTheTvDb	theTvDbId		ID
# getSeriesSeasons		serieKey		dict of MediaInfo
# getSeriesEpisodes		serieKey=None		list of MediaInfo
#				season=None
# getSeriesEpisode		serieKey,season,episode	MediaInfo
# getSeriesCount					Count
# getSeriesCountSeasons		serieKey		Count
# getEpisodesCount		mediaId,season		Count
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
#from FailedEntry import FailedEntry
from MediaInfo import MediaInfo
import Utf8

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
	
DB_SQLITE_LOADED = False
DATABASE_HANDLER_FOUND = False

try:
	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PVS_DatabaseHandlerSQL import databaseHandlerSQL
	from PVS_DatabaseHandlerSQL import databaseHandlerSQL
	DB_SQLITE_LOADED = True
	printl("PVS_DatabaseHandlerSQL Loaded    :) ", None, "H")	
	DATABASE_HANDLER_FOUND = True
except Exception, ex:
	printl("PVS_DatabaseHandlerSQL not Loaded :(   "+ str(ex), None , "H")
		
try:					   
	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PVS_DatabaseHandlerPICKLE import databaseHandlerPICKLE
	from PVS_DatabaseHandlerPICKLE import databaseHandlerPICKLE
	printl("PVS_DatabaseHandlerPICKLE Loaded :)", None, "H")
	DATABASE_HANDLER_FOUND = True
except Exception, ex:
	printl("PVS_DatabaseHandlerPICKLE not Loaded :(   "+ str(ex), None, "H")
		
try:
	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PVS_DatabaseHandlerTXD import databaseHandlerTXD
	from PVS_DatabaseHandlerTXD import databaseHandlerTXD
	printl("PVS_DatabaseHandlerTXD Loaded    :)", None, "H")
	DATABASE_HANDLER_FOUND = True
except Exception, ex:
	printl("PVS_DatabaseHandlerTXD not Loaded :(   "+ str(ex), None, "H")
	
if DATABASE_HANDLER_FOUND != True:
	printl("Exception: no DatabaseLoader installed :(   ", None, "E")

#------------------------------------------------------------------------------------------

gDatabase = None
gDatabaseMutex = Lock()

class Database(object):
	DB_NONE   = 0
	DB_TXD    = 2
	DB_PICKLE = 3
	DB_SQLITE = 4

	DB_PATH   = config.plugins.pvmc.configfolderpath.value

	if DB_SQLITE_LOADED and os.path.exists(DB_PATH + "usesql"):
		USE_DB_TYPE    	= DB_SQLITE
	else:
		USE_DB_TYPE    	= DB_PICKLE
		
	USE_BACKUP_TYPE = DB_NONE  	# To do: will always backup to DB_PICKLE ????
	
	USE_INDEXES = False  		# Create indexes key/id
	PRELOADDB   = True  		# Reload All tables on Start (default)
	# NOTE: almost every queries to DB force to use all tables
	#  Examples:
	#  	 Count Records(webif)
	#  	 checkduplicates
	
	CONFIGKEY  = -999999
	
	def __init__(self):
		printl("->", self, "S")
			
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
	
	def __str__(self):
		printl("->", self, "S")	
		try:
			rtv = unicode(self.getMediaCount(MediaInfo.MOVIE)) + \
					u" " + \
					unicode(self.getMediaCount(MediaInfo.SERIE)) + \
					u" " + \
					unicode(self.getEpisodesCount())
			return Utf8.utf8ToLatin(rtv)
		except Exception, ex:
			printl("Error retriving _str_: "+ str(ex), self, "W")
			return "Error retriving _str_"			

	def importDataToSql (self):
		printl("->", self, "S")
		#try:
		#	printl("Importing Data", self)
		#	#self.preload()	# Load from PICKLE
		#	dbHandlerPickle = databaseHandlerPICKLE().getInstance()
		#	#dbHandlerSql 	= databaseHandlerSQL().getInstance("ImportDataToSql")
		#	self.dbHandler.overwriteDB(dbHandlerPickle.get_Movies(),dbHandlerPickle.get_Series(),dbHandlerPickle.get_SeriesEpisodes())
		#	
		#	self.save()  	# save to Database SQL
		#	try:
		#		pass #os.rename(self.DB_TXD, self.DB_TXD +'.'+ str(time.time()) + '.bak')
		#	except Exception, ex:
		#		printl("Backup movie txd failed! Ex: " + str(ex), __name__, "E")
		#except Exception, ex:
		#	printl("Failed Import to SQL! Reloading Pickles Ex: " + str(ex), __name__, "E")
		#	self.dbHandler = databaseHandlerPICKLE().getInstance()
		#	#self.reload()	# Load from PICKLE
			

	def setDBType(self, version):
		printl("->", self, "S")
		self.USE_DB_TYPE = version
		printl("DB Type set to " + str(version), self)

	def getDBTypeText(self):
		printl("->", self, "S")
		if self.USE_DB_TYPE == self.DB_TXD:
			return "TXD"
		elif self.USE_DB_TYPE == self.DB_PICKLE:
			return "Pickle"
		elif self.USE_DB_TYPE == self.DB_SQLITE:
			return "SQLite"
		else:
			return "No DB Type defined"

	def getInstance(self):
		printl("->", self, "S")
		global gDatabase
		global gDatabaseMutex
		
		if gDatabase is None:
			printl("Acquiring Mutex", self, "I")
			gDatabaseMutex.acquire()
			try:
				printl("Creating new Database instance", self)				
				if self.PRELOADDB:
					self.preload()  # RELOAD ALLL 
					
				gDatabase = self
			finally:	
				gDatabaseMutex.release()
				printl("Released Mutex", self, "I")
		
		return gDatabase

	def preload(self):
		printl("->", self, "S")
		self.dbHandler.loadAll()
		
	def deleteMissingFiles(self):
		printl("->", self, "S")
		self._verifyAndDeleteMissingFiles( self.dbHandler.getMediaValues(MediaInfo.MOVIE) )
		self._verifyAndDeleteMissingFiles( self.dbHandler.getMediaValues(MediaInfo.EPISODE) )
		self._verifyAndDeleteMissingFiles( self.dbHandler.getMediaValues(MediaInfo.FAILEDSYNC) )

	def _verifyAndDeleteMissingFiles(self, records):
		listMissing = []
		for m in records:
			path = m.Path + u"/" + m.Filename + u"." + m.Extension
			if os.path.exists(Utf8.utf8ToLatin(path)) is False:
				listMissing.append(m)
                                
		printl("Missing: " + str(len(listMissing)), self)
		for m in listMissing:
			self.remove(m)

	def remove(self, media, is_Movie=False, is_Serie=False, is_Episode=False):
		printl("->", self, "S")
		printl("is Movie=" + str(media.isTypeMovie()) + " is Serie=" + str(media.isTypeSerie()) + " is Episode=" + str(media.isTypeEpisode()), self)

		return self.dbHandler.deleteMedia(media.MediaType, media.Id)
	
	##
	# Adds media files to the db
	# @param media: The media file
	# @return: mediaID in exist/inserted  or  -1 in case of error
	def add(self, media):
		printl("->", self, "S")
		return self.dbHandler.insertMedia(media)

	def save(self):
		printl("->", self, "S")
		global gDatabaseMutex
		printl("Acquiring Mutex", self, 4)
		gDatabaseMutex.acquire()
		try:
			printl("Acquired Mutex", self, 4)
			# Always safe pickel as this increses fastsync a lot
			
			# will be the backup
			#self.savePickel() 
			
			self.dbHandler.saveMediaFiles()
		
			return True
		except Exception, ex:
			printl("Failed Save! Ex: " + str(ex), __name__, "E")
			return False
		finally:	
			gDatabaseMutex.release()
			printl("Released Mutex", self, "I")
		
#
#################################   MEDIAS   ################################# 
#
	def getMediaValues(self, type, order=None, firstRecord=0, numberOfRecords=9999999):
		printl("->", self, "S")
		return self.dbHandler.getMediaValues(type, order, firstRecord, numberOfRecords)

	#
	# DML statements
	#	
	def insertMediaWithDict(self, key_value_dict):
		printl("->", self, "S")
		return self.dbHandler.insertMediaWithDict(key_value_dict)
	
	def updateMediaWithDict(self, key_value_dict):	#ID is Required
		printl("->", self, "S")
		return self.dbHandler.updateMediaWithDict(key_value_dict)
	
	def deleteMedia(self, type, id):
		printl("->", self, "S")
		return self.dbHandler.deleteMedia(type, id)

#
#################################   MOVIES   ################################# 
#
	def getDbDump(self):
		printl("->", self, "S")
		return self.dbHandler.getDbDump()
	
	def dbIsCommited(self):
		printl("->", self, "S")
		return self.dbHandler.dbIsCommited()

	def getMediaWithId(self, id):
		printl("->", self, "S")
		return self.dbHandler.getMediaWithId(id)

	def getMediaWithImdbId(self, imdbid):
		printl("->", self, "S")
		return self.dbHandler.getMediaWithImdbId(imdbid)

	def getMediaWithTheTvDbId(self, thetvdbid):
		printl("->", self, "S")
		return self.dbHandler.getMediaWithTheTvDbId(thetvdbid)

	def getMediaCount(self, type):
		printl("->", self, "S")
		return self.dbHandler.getMediaCount(type)	
	
	def setMoviesSeen(self, id):
		printl("->", self, "S")
		return 	
#	
#################################   SERIES   ################################# 
#
	def getEpisodesCount(self, mediaId=None, season=None):
		return self.dbHandler.getEpisodesCount(mediaId, season)
	
	# DML statements
	def insertSerie(self, media):
		printl("->", self, "S")
		return self.dbHandler.insertSerie(media)

	#def insertSerieWithDict(self, key_value_dict):
	#	printl("->", self, "S")
	#	return self.dbHandler.insertSerieWithDict(key_value_dict)
	#
	#def updateSerieWithDict(self, key_value_dict):		#ID is Required
	#	printl("->", self, "S")
	#	return self.dbHandler.updateSerieWithDict(key_value_dict)
	#
	#def deleteSerie(self, id):
	#	printl("->", self, "S")
	#	return self.dbHandler.deleteSerie(id)

#	
################################   EPISODES   ################################ 
#
	def getEpisode(self, id):
		printl("->", self, "S")
		return self.dbHandler.getMediaWithId(id)

	def getEpisodes(self, mediaId=None):
		printl("->", self, "S")
		return self.dbHandler.getEpisodes(mediaId)
	#TODO: CONVERT TO ID	
	def getEpisodesWithTheTvDbId(self, theTvDbId, season=None):
		printl("->", self, "S")
		Id = self.dbHandler.getMediaWithTheTvDbId(theTvDbId).Id
		return self.dbHandler.getEpisodes(Id, season)
	
#	
#################################   FAILED   ################################# 
#
	def getFailed(self):
		printl("->", self, "S")
		return self.dbHandler.getMediaValues(MediaInfo.FAILEDSYNC)

	def clearFailed(self):
		printl("->", self, "S")
		return self.dbHandler.deleteFailed()

#
###################################  UTILS  ###################################
#
	##
	# Checks if file is already in the db
	# @param path: utf-8 
	# @param filename: utf-8 
	# @param extension: utf-8 
	# @return: True if already in db, False if not
	def checkDuplicate(self, path, filename, extension):
		#printl("->", self, "S")
		return self.dbHandler.checkDuplicateMF(path, filename, extension)

	def transformGenres(self):
		printl("->", self, "S")
		self.dbHandler.transformGenres()
	
#	
############################################################################## 
#
	# NOT USED ???
	#def searchDeleted(self):
	#	printl("->", self, 10)
	#	movies = self.getMovies()
	#
	#	for key in movies:
	#		m = movies[key]
	#		path = m.Path + u"/" + m.Filename + u"." + m.Extension
	#		if os.path.exists(Utf8.utf8ToLatin(path)) is False:
	#			printl(":-( " + Utf8.utf8ToLatin(path), self)
	#	
	#	series = self.getSeries()
	#	episodes = self.episodesGet()
	#	for key in series:
	#		if key in episodes:
	#			for season in episodes[key]:
	#				for episode in episodes[key][season]:
	#					m = episodes[key][season][episode]
	#					path = m.Path + u"/" + m.Filename + u"." + m.Extension
	#					if os.path.exists(Utf8.utf8ToLatin(path)) is False:
	#						printl(":-( " + Utf8.utf8ToLatin(path), self)

	#not tested
	#self.idxMoviesByImdb = {}
	#self.idxSeriesByTheTvDb = {}
	#def createMoviesIndexes(self):
	#	printl("->", self, 10)
	#	start_time = time.time()
	#	self.idxMoviesByImdb = {}
	#	for key in self._dbMovies:
	#		if key != self.CONFIGKEY:		# only for Pickle
	#			self.idxMoviesByImdb[self._dbMovies[key].ImdbId] = key
	#	elapsed_time = time.time() - start_time
	#	printl("Indexing Took : " + str(elapsed_time), self, 11)

	#not tested
	#def createSeriesIndexes(self):
	#	printl("->", self, 10)
	#	start_time = time.time()
	#	self.idxSeriesByTheTvDb = {}
	#	for key in self._dbSeries:
	#		self.idxSeriesByTheTvDb[self._dbSeries[key].TheTvDbId] = key
	#	elapsed_time = time.time() - start_time
	#	printl("Indexing Took : " + str(elapsed_time), self)

	#def createSeriesIndexes(self):
	#	start_time = time.time()
	#	for key in self._dbSeries:
	#		self.idxSeriesByThetvdb[self._dbSeries[key].TheTvDbId] = key
	#	elapsed_time = time.time() - start_time
	#	printl("Indexing Took : " + str(elapsed_time), self)
