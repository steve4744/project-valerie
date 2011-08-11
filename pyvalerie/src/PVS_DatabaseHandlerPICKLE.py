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
#   v0 - ../06/2011 - Zuki - Let's import the Pickle Interface from database.py
#
#   v1 - 15/07/2011 - Zuki - added Config Record to pickle's to save the structure version
#			   - added Upgrade Database function's (to apply conversions)
#
#   v2 - 16/07/2011 - Zuki - upgrade database is now working
#			     DB Patch 1 will update fields MediaInfo.MediaType
#
#   v
#
#   v
#
#   v
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import time
import cPickle   as pickle
from Components.config import config
from   MediaInfo         import MediaInfo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__common__ import log as log
import Genres

gDatabaseHandler = None
gConnection = None

class databaseHandlerPICKLE(object):
	DB_PATH           = config.plugins.pvmc.configfolderpath.value

	FAILEDDB   = DB_PATH + "failed.db"
	MOVIESDB   = DB_PATH + "movies.db"
	TVSHOWSDB  = DB_PATH + "tvshows.db"
	EPISODESDB = DB_PATH + "episodes.db"

	TESTDB     = DB_PATH + "test.db"
	CONFIGKEY  = -999999
	DB_VERSION = 1
	IDMODEAUTO = False

	USE_INDEXES = False  	# Create indexes key/id
	AUTOCOMMIT  = False	# Only if database have a few record... 500?
				# It can be changed on runtime (to avoid commit during sync )
	MoviesCommited   = True
	SeriesCommited   = True
	EpisodesCommited = True
	FailedCommited 	 = True
	
	ORDER_TITLE = 1
	ORDER_YEAR  = 2

	_dbMovies   = None
	_dbSeries   = None
	_dbEpisodes = None	
	_dbFailed   = None

	_addFailedCauseOf = None

	def __init__(self):
		printl("->", self)
		
	def getInstance(self):
		log("->", self, 10)
		global gDatabaseHandler
		if gDatabaseHandler is None:			
			printl("PICKLE - New Instance", self)
			gDatabaseHandler = self
		return gDatabaseHandler

	def dbIsCommited(self):
		return self.MoviesCommited and self.SeriesCommited and self.EpisodesCommited and self.FailedCommited
#
#################################   MOVIES   ################################# 
#
	def _loadMoviesDB(self):
		log("->", self, 10)
		if self._dbMovies is None:
			start_time = time.time()
			self._dbMovies = {}
			try:
				if os.path.exists(self.MOVIESDB):
					fd = open(self.MOVIESDB, "rb")
					self._dbMovies = pickle.load(fd)
					fd.close()
					self._upgradeMovies(self._dbMovies)
				else:
					self.setDBVersion(self._dbMovies, self.DB_VERSION)
	
			except Exception, ex:
				print ex
				print '-'*60
				import sys, traceback
				traceback.print_exc(file=sys.stdout)
				print '-'*60
					
			elapsed_time = time.time() - start_time
			log("LoadMovies Took : " + str(elapsed_time), self, 11)
					
			if self.USE_INDEXES:
				start_time = time.time()
				self.createMoviesIndexes()
				elapsed_time = time.time() - start_time
				log("Indexing Took : " + str(elapsed_time), self, 11)
				
			#for movieKey in self._dbMovies:
			#	if movieKey != self.CONFIGKEY:
			#		if IDMODEAUTO:
			#			self._dbMovies[movieKey].Id = movieKey
			#		else:
			#			self._dbMovies[movieKey].Id = self._dbMovies[movieKey].ImdbId


	def saveMovies(self):		
		printl("->", self)
		if self.MoviesCommited:
			printl("Nothing to Commit", self)
			return
		start_time = time.time()
		try:		
			fd = open(self.MOVIESDB, "wb")
			pickle.dump(self._dbMovies, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			self.MoviesCommited = True
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (movies.db): " + str(elapsed_time), self)

	def _moviesCheckLoaded(self):
		#log("->", self, 10)
		if self._dbMovies is None:
			log("Movies Not Loaded", self, 10)
			self._loadMoviesDB()

	def getMovies(self):
		printl("->", self)
		newList	= {}
		self._moviesCheckLoaded()
		start_time = time.time()
		newList	= self._dbMovies.copy()
		if self.CONFIGKEY in newList:		# only for Pickle
			del newList[self.CONFIGKEY]
					
		elapsed_time = time.time() - start_time

		#printl("2 --------------------------------")			
		#for key in newList:
		#	printl(repr(newList[key].Title))
		
		printl("Took: " + str(elapsed_time), self)
		return newList # return always a copy, user don't use db

	def getMoviesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
		printl("->", self)
		if order is None:
			order = self.ORDER_TITLE;
		listToSort   = []
		listSorted   = []
		listToReturn = []
		
		self._moviesCheckLoaded()
		if self._dbMovies is not None:
			start_time = time.time()
		
			for movieKey in self._dbMovies:
				if movieKey != self.CONFIGKEY:
					listToSort.append(self._dbMovies[movieKey])
						
			#printl("1 --------------------------------")
			#print (str(listToSort))
			
			# sort by ....
			if order == self.ORDER_TITLE:
				listSorted = sorted(listToSort, key=lambda k: k.Title)				
			elif order == self.ORDER_YEAR:
				listSorted = sorted(listToSort, key=lambda k: k.Year)
			else:
				listSorted = listToSort
			#printl("2 --------------------------------")
			#print (str(listSorted))					

			## return parcial listToReturn ---- (on Dict - orderdict only on 2.7)
			if firstRecord==0 and numberOfRecords==9999999:
				printl("All Records", self)
				listToReturn = listSorted
			else:				
				recPosition = 0
				recCount = 0
				for item in listSorted:
					if recPosition >= firstRecord:
						listToReturn.append(item)
						recCount += 1
					recPosition += 1
					if recCount >= numberOfRecords:
						break
			#printl("3 --------------------------------")
			#print (str(listSorted))					

						
							
			elapsed_time = time.time() - start_time		
			printl("Took: " + str(elapsed_time), self)

		return listToReturn

	def getMoviesCount(self):
		log("->", self, 20)
		self._moviesCheckLoaded()
		return len(self.getMovies())
		
	def getMoviesWithKey(self, movieKey):
		log("->", self, 15)
		self._moviesCheckLoaded()
		start_time = time.time()
		element = None
		if movieKey in self._dbMovies:
			log("Movie Exists", self, 18)
			element = self._dbMovies[movieKey]
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return element

	def getMovieKeyWithImdbId(self, imdbId):
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

	def insertMovie(self, media):
		log("->", self, 20)
		self._moviesCheckLoaded()
		movieKey = media.ImdbId
		#movieKey = media.Id
		if not movieKey in self._dbMovies:
			self.MoviesCommited = False
			self._dbMovies[movieKey] = media
			if self.AUTOCOMMIT:
				self.saveMovies()
			return True	
		else: 
			self._addFailedCauseOf = self._dbMovies[movieKey]
			return False
			
	def deleteMovie(self, movieKey):
		log("->", self, 20)
		self._moviesCheckLoaded()
		if movieKey in self._dbMovies:
			self.MoviesCommited = False
			del(self._dbMovies[movieKey])	
			if self.AUTOCOMMIT:
				self.saveMovies()
			return True
		else:
			return False

	def updateMovie(self, movieKey, media):
		log("->", self, 20)
		self._moviesCheckLoaded()
		return True
		
#	
#################################   SERIES   ################################# 
#

	def _loadSeriesEpisodesDB(self):
		log("->", self, 10)
		start_time = time.time()
		if self._dbSeries is None or self._dbEpisodes is None:
			self._dbSeries 	 = self._getAllSeries()
			self._dbEpisodes = self._getAllEpisodes()
			if self.USE_INDEXES:
				self.createSeriesIndexes()
			
			#printl("3 --------------------------------")			
			#for key in self._dbSeries:
			#	if key != self.CONFIGKEY:		# only for Pickle
			#		printl(repr(self._dbSeries[key].Title))
				
		# Let's avoid refer to 0 as key... why this happen???
		#	don't clean ghostfiles to create problems
		#	
		# FIX: GHOSTFILES
		#if self._dbEpisodes.has_key("0"):
		#	ghost = self._dbEpisodes["0"].values()
		#	for season in ghost:
		#		for episode in season.values():
		#			self.remove(episode)
		#	if self._dbEpisodes.has_key("0"):
		#		del self._dbEpisodes["0"]
		#
		#for serie in self._dbEpisodes:
		#	if serie != self.CONFIGKEY: #not ConfigRecord
		#		for seasonKey in self._dbEpisodes[serie]:
		#			season = self._dbEpisodes[serie][seasonKey]
		#			for episodeKey in season:
		#				episode = season[episodeKey]
		#				if type(episode) is MediaInfo:
		#					if not episode.isTypeEpisode():
		#						b = self.remove(episode, isEpisode=True)
		#						printl("RM: " + str(b), self)
				
		elapsed_time = time.time() - start_time
		printl("Load Series/Episodes Took : " + str(elapsed_time), self)

	def _getAllSeries(self):
		printl("->", self)
		records = {}
		try:
			if os.path.exists(self.TVSHOWSDB):
				fd = open(self.TVSHOWSDB, "rb")
				records = pickle.load(fd)
				fd.close()
				self._upgradeSeries(records)
			else:
				self.setDBVersion(records, self.DB_VERSION)
				
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		return (records)

	def _getAllEpisodes(self):
		printl("->", self)
		records = {}
		try:
			if os.path.exists(self.EPISODESDB):
				fd = open(self.EPISODESDB, "rb")
				records = pickle.load(fd)
				fd.close()
				self._upgradeEpisodes(records)
			else:
				self.setDBVersion(records, self.DB_VERSION)
				
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60

		return (records)
		
	#Call when data is needed, to verify if is loaded
	def _seriesCheckLoaded(self):
		log("->", self, 15)
		if self._dbSeries is None:
			self._loadSeriesEpisodesDB()

	#								    #	
	#   PUBLIC FUNCTIONS	# # # # # # # # # # # # # # # # # # # # # # # 
	#								    #	
	
	def saveSeries(self):		
		printl("->", self)
		if self.SeriesCommited:
			printl("Nothing to Commit", self)
			return
			
		start_time = time.time()
		try:		
			fd = open(self.TVSHOWSDB, "wb")
			pickle.dump(self._dbSeries, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			SeriesCommited = True
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (tvshows.db): " + str(elapsed_time), self)
		
	def saveEpisodes(self):		
		printl("->", self)
		if self.EpisodesCommited:
			printl("Nothing to Commit", self)
			return
		start_time = time.time()
		try:		
			fd = open(self.EPISODESDB, "wb")
			pickle.dump(self._dbEpisodes, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			EpisodesCommited = True
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (episodes.db): " + str(elapsed_time), self)


	def getSeries(self, order=None, firstRecord=0, numberOfRecords=9999999):
		printl("->", self)
		newList	= {}
		self._seriesCheckLoaded()
		if self._dbSeries is not None:
			newList	= self._dbSeries.copy()
			if self.CONFIGKEY in newList:
				del newList[self.CONFIGKEY]
		printl("<-", self)
		return newList # return always a copy, user don't use db

	def getSeriesCount(self):
		log("->", self, 20)
		self._seriesCheckLoaded()
		return len(self.getSeries())
		
	def getSeriesCountSeasons(self, serieKey):
		log("->", self, 15)
		self._seriesCheckLoaded()
		count = None
		if serieKey in self._dbEpisodes:
			count = len(self._dbEpisodes[serieKey])
		return count
	
	def getSeriesCountEpisodes(self, serieKey=None, season=None):
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
			
	def getSeriesWithKey(self, serieKey):
		log("->", self, 15)
		self._seriesCheckLoaded()
		start_time = time.time()
		element = None
		if serieKey in self._dbSeries:
			log("Serie Exists", self, 18)
			element = self._dbSeries[serieKey]
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return element

	def getSeriesKeyWithTheTvDbId(self, theTvDbId):
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
					if self._dbSeries[serieKey].TheTvDbId == theTvDbId:
						key = serieKey
						break
		
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return key

	def getSeriesEpisodesValues(self):
		log("->", self, 15)
		self._seriesCheckLoaded()
		list = []
		for serieKey in self._dbEpisodes:
			if serieKey != self.CONFIGKEY:
				for season in self._dbEpisodes[serieKey]:
					list += self._dbEpisodes[serieKey][season].values()
		return list

	def getSeriesEpisodes(self, serieKey=None, season=None):
		log("->", self, 15)
		self._seriesCheckLoaded()
		if serieKey is None:		# seriesGetAllEpisodes
			newList	= {}			
			if self._dbEpisodes is not None:
				newList	= self._dbEpisodes.copy()
				if self.CONFIGKEY in newList:
					del newList[self.CONFIGKEY]
			return newList
		
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

	def getSeriesEpisode(self, serieKey, season, episode):
		log("->", self, 15)
		self._seriesCheckLoaded()
		element = None
		if serieKey in self._dbEpisodes:
			if season in self._dbEpisodes[serieKey]:
				if episode in self._dbEpisodes[serieKey][season]:
					element = self._dbEpisodes[serieKey][season][episode]
		return element
	
	def getSeriesSeasons(self, serieKey):
		log("->", self, 15)
		self._seriesCheckLoaded()
		if serieKey in self._dbEpisodes:
			return self._dbEpisodes[serieKey].keys()
				
		return self.seriesGetAll().values()


	def insertSerie(self, media):
		log("->", self, 20)
		self._seriesCheckLoaded()
		serieKey = media.TheTvDbId
		#serieKey = media.Id
		#if USE_INDEXES:
		#	if self.idxSeriesByThetvdb.has_key(media.TheTvDbId) is None:
			
		#else:
		
		if self._dbSeries.has_key(serieKey) is False:
			self.SeriesCommited = False
			self._dbSeries[serieKey] = media
			if self.AUTOCOMMIT:
				self.saveSeries()
			return True
		else:
			#self._addFailedCauseOf = self._dbSeries[media.TheTvDbId]
			#return False
			return True # We return true here cause this is not a failure but simply means that the tvshow already exists in the db

	def insertEpisode(self, media):
		log("->", self, 20)
		self._seriesCheckLoaded()
		serieKey = media.TheTvDbId
		#printl("serie: "+serieKey+ " season: " + str(media.Season) + " Episode: "+str(media.Episode))
		#serieKey = media.Id
		self.EpisodesCommited = False
		
		if self._dbEpisodes.has_key(serieKey) is False:
			self._dbEpisodes[serieKey] = {}
		
		if self._dbEpisodes[serieKey].has_key(media.Season) is False:
			self._dbEpisodes[serieKey][media.Season] = {}
		
		if self._dbEpisodes[serieKey][media.Season].has_key(media.Episode) is False:
			self._dbEpisodes[serieKey][media.Season][media.Episode] = media			
		else:
			self._addFailedCauseOf = self._dbEpisodes[serieKey][media.Season][media.Episode]
			return False
		
		if self.AUTOCOMMIT:
			self.saveEpisodes()
		return True
			
	def deleteSerie(self, serieKey): # for compability, not consistent
		log("->", self, 10)
		self._seriesCheckLoaded()
		if serieKey in self._dbSeries:	
			self.SeriesCommited = False
			del(self._dbSeries[serieKey])
			if self.AUTOCOMMIT:
				self.saveSeries()
		return True
			
	def deleteSerieCascade(self, serieKey):
		log("->", self, 10)
		self._seriesCheckLoaded()
		if serieKey in self._dbEpisodes:
			self.EpisodesCommited = False
			del(self._dbEpisodes[serieKey])
			if self.AUTOCOMMIT:
				self.saveEpisodes()
		if serieKey in self._dbSeries:	
			self.SeriesCommited = False
			del(self._dbSeries[serieKey])
			if self.AUTOCOMMIT:
				self.saveSeries()
		return True
	
	#def updateSerie(self, movieKey, media):
	#	log("->", self, 20)
	#	self._seriesCheckLoaded()
	#	self.SeriesCommited = False
	#	return True
		
	def deleteEpisode(self, serieKey, season, episode):
		log("->", self, 10)
		self._seriesCheckLoaded()
		if serieKey in self._dbEpisodes:
			if season in self._dbEpisodes[serieKey]:
				if episode in self._dbEpisodes[serieKey][season]:
					self.EpisodesCommited = False
					del(self._dbEpisodes[serieKey][season][episode])
					if len(self._dbEpisodes[serieKey][season]) == 0:
						del(self._dbEpisodes[serieKey][season])
					if len(self._dbEpisodes[serieKey]) == 0:
						del(self._dbEpisodes[serieKey])
						if self._dbSeries.has_key(serieKey) is True:
							self.SeriesCommited = False
							del(self._dbSeries[serieKey])
					if self.AUTOCOMMIT:
						self.saveSeries()
						self.saveEpisodes()
					return True
		return False
#	
#################################   FAILED   ################################# 
#
	def _loadFailedDB(self):
		printl("->", self)
		start_time = time.time()		
		try:		
			if os.path.exists(self.FAILEDDB):
				fd = open(self.FAILEDDB, "rb")
				self._dbFailed = pickle.load(fd)
				fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (failed.db): " + str(elapsed_time), self)
		
		return (self._dbFailed)



	def _failedCheckLoaded(self):
		log("->", self, 10)
		if self._dbFailed is None:
			log("Failed Not Loaded", self, 10)
			self._loadFailedDB()

#	def dbIsCommited(self):
#		return self.FailedCommited

	def getFailed(self):
		printl("->", self)
		newList	= []
		self._failedCheckLoaded()
		if self._dbFailed is not None:
			newList	= self._dbFailed #.copy()
			#if self.CONFIGKEY in newList:		# only for Pickle
			#	del newList[self.CONFIGKEY]			
		printl("<-", self)
		return newList # return always a copy, user don't use db

	def getFailedCount(self):
		log("->", self, 20)
		self._failedCheckLoaded()
		return len(self.getFailed())

		
	def saveFailed(self):
		printl("->", self)
		if self.FailedCommited:
			printl("Nothing to Commit", self)
			return
		start_time = time.time()
		try:		
			fd = open(self.FAILEDDB, "wb")
			pickle.dump(self._dbFailed, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			self.FailedCommited = True
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
	
		elapsed_time = time.time() - start_time
		printl("Took (failed.db): " + str(elapsed_time), self)
		
	#def saveFailed2(self):
	#	pass

	def insertFailed(self, entry):
		log("->", self, 20)
		self.FailedCommited = False
		self._dbFailed.append(entry)
		if self.AUTOCOMMIT:
			self.saveFailed()
		return True	
			
	def deleteFailed(self, entry=None):
		log("->", self, 20)
		if entry is None:
			try:
				self.FailedCommited = False
				if self._dbFailed is None:
					self._dbFailed = []
				else:
					del self._dbFailed[:]
			except Exception, ex:
				log("Exception: " + str(ex), self, 2)

			if self.AUTOCOMMIT:
				self.saveFailed()
			return True
		else:
			if entry in self._dbFailed:
				self.FailedCommited = False
				self._dbFailed.remove(entry)
			if self.AUTOCOMMIT:
				self.saveFailed()
			return True

###################################  UTILS  ###################################

	def checkDuplicate(self, path, filename, extension):
		self._moviesCheckLoaded()
		self._seriesCheckLoaded()
		self._failedCheckLoaded()
		for key in self._dbMovies:
			if key == self.CONFIGKEY:		# only for Pickle
				continue
			if self._dbMovies[key].Path == path:
				if self._dbMovies[key].Filename == filename:
					if self._dbMovies[key].Extension == extension:
						return self._dbMovies[key]
		
		for key in self._dbSeries:
			if key == self.CONFIGKEY:		# only for Pickle
				continue
			if key in self._dbEpisodes:
				for season in self._dbEpisodes[key]:
					for episode in self._dbEpisodes[key][season]:
						if self._dbEpisodes[key][season][episode].Path == path:
							if self._dbEpisodes[key][season][episode].Filename == filename:
								if self._dbEpisodes[key][season][episode].Extension == extension:
									printl("DUPLICATE: " + path +" "+ filename+" "+  extension, self);
									return self._dbEpisodes[key][season][episode]
		
		return None

	def transformGenres(self):
		for key in self.getMovies():
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

		for key in self.getSeries():
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



	
############################  DB VERSION CONTROL  #############################
	def getDBVersion(self, records):
		if records.has_key(self.CONFIGKEY):
			return records[self.CONFIGKEY]
		else:
			printl ("DB without version")
			return 0
		
	def setDBVersion(self, records, version):
		records[self.CONFIGKEY] = version
		printl ("DB version set to "+ str(version))
		
############################    UPGRADE MOVIES    #############################
	def _upgradeMovies(self, records):
		printl("->",self)
		currentDBVersion = self.getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_m_1(records)
					self.setDBVersion(records, updateToVersion)
					
				elif updateToVersion==2:
					#self._upgrade_m_2(records)
					#self.setDBVersion(records, updateToVersion)
					pass
				elif updateToVersion==3:
					pass		
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass
				
			self.saveMovies()
	
	# Migrate isMovie,isSerie,isEpisode to MediaType (1,2,3)
	# can be used by movies.db and tvshows.db
	def _upgrade_m_1(self, records):
		for rec in records:
			if type(records[rec]) is MediaInfo:
				records[rec].getMediaType() # will populate mediatype field
			
	def _upgrade_m_2(self, records):
		pass
	
############################    UPGRADE SERIES    #############################
	def _upgradeSeries(self, records):
		printl("->",self)
		currentDBVersion = self.getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_m_1(records) #use Movies upgrade
					self.setDBVersion(records, updateToVersion)
					
				elif updateToVersion==2:
					pass
				elif updateToVersion==3:
					pass
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass
				
			self.saveSeries()
	
	def _upgrade_s_2(self, records):
		pass
	
############################    UPGRADE EPISODES    #############################
	def _upgradeEpisodes(self, records):
		printl("->",self)
		currentDBVersion = self.getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_e_1(records) #use Movies upgrade
					self.setDBVersion(records, updateToVersion)
				elif updateToVersion==2:
					pass					
				elif updateToVersion==3:
					pass
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass

			self.saveEpisodes()


	def _upgrade_e_1(self, records):
		for serie in records:
			for season in records[serie]:
				for episode in records[serie][season]:
					if type(records[serie][season][episode]) is MediaInfo:
						records[serie][season][episode].getMediaType() # will populate mediatype field
			







#########################################################################
		#self.doTest_DuplicateTestDB()
		#printl("TEST 1 ************************************************", self)
		#self.doTest_Speed()
		#printl("TEST 2 ************************************************", self)
		#self.doTest_Speed()
		#printl("TEST 3 ************************************************", self)
		#self.doTest_Speed()
		#printl("TEST 4 ************************************************", self)
		#self.doTest_Speed()
		#printl("TEST 5 ************************************************", self)
		
	def doTest_DuplicateTestDB(self):
		printl("->", self)
		start_time = time.time()
		if os.path.exists(self.TESTDB):
			fd = open(self.TESTDB, "rb")
			records = pickle.load(fd)
			fd.close()
		elapsed_time = time.time() - start_time
		printl("Read Took (TESTDB): " + str(elapsed_time), self)

		cnt=0			
		db2 = {}
		start_time = time.time()
		for key in records:
			db2[cnt] = records[key]
			cnt+=1
		for key in records:
			db2[cnt] = records[key]
			cnt+=1
		elapsed_time = time.time() - start_time
		printl("final DB: "+str(cnt)+" records. Took: " + str(elapsed_time), self)

		start_time = time.time()
		fd = open(self.TESTDB, "wb")
		pickle.dump(db2, fd, pickle.HIGHEST_PROTOCOL)
		fd.close()
		elapsed_time = time.time() - start_time
		printl("Write New TestDB. Took : " + str(elapsed_time), self)
		
	def doTest_Speed(self):
		printl("->", self)
		start_time = time.time()
		if os.path.exists(self.TESTDB):
			fd = open(self.TESTDB, "rb")
			records = pickle.load(fd)
			fd.close()
		elapsed_time = time.time() - start_time
		printl("Read test.db with " +str(len(records))+" records. Took: " + str(elapsed_time), self)

		start_time = time.time()
		cnt=0
		for key in records:
			records[key].Id = "blab1341414141cvbgdfghdfg24123123123la"
			cnt+=1
		elapsed_time = time.time() - start_time
		printl("change "+str(cnt)+" records, Took : " + str(elapsed_time), self)

		start_time = time.time()
		cnt=0
		for key in records:
			if records.has_key(key):
				records[key].Id = "blab1341414141cvbgdfghdfg24123123123lb"
				cnt+=1
		elapsed_time = time.time() - start_time
		printl("Change "+str(cnt)+" records, using -Has_key- Took : " + str(elapsed_time), self)

		start_time = time.time()
		cnt=0
		for key in records:
			if key in records:
				records[key].Id = "blab1341414141cvbgdfghdfg24123123123lc"
				cnt+=1
		elapsed_time = time.time() - start_time
		printl("Change "+str(cnt)+" records, using -key in- Took : " + str(elapsed_time), self)

		dbTest = {}
		start_time = time.time()
		cnt=0
		for key in records:
			dbTest[key] = records[key]
			cnt+=1
			
		elapsed_time = time.time() - start_time
		printl("Duplicate "+str(cnt)+" records, Took : " + str(elapsed_time), self)

		for key in records:
			if records[key].ImdbId == "tt99009900":
				records[key].Id = "blab1341414141cvbgdfghdfg24123123123lb"
				cnt+=1
		elapsed_time = time.time() - start_time
		printl("Query "+str(cnt)+" records, using -if equal- Took : " + str(elapsed_time), self)

