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
import datetime
import cPickle   as pickle
from Components.config import config
from   MediaInfo         import MediaInfo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__common__ import log as log
import Genres
import random
gDatabaseHandler = None
gConnection = None

class databaseHandlerPICKLE(object):
	DB_PATH           = config.plugins.pvmc.configfolderpath.value

	MEDIAFILESDB = DB_PATH + "mediafiles.db"

	FAILEDDB   = DB_PATH + "failed.db"
	MOVIESDB   = DB_PATH + "movies.db"
	TVSHOWSDB  = DB_PATH + "tvshows.db"
	EPISODESDB = DB_PATH + "episodes.db"


	TESTDB     = DB_PATH + "test.db"
	CONFIGKEY  = -999999
	DB_VERSION = 1
	IDMODEAUTO = True	# Tested... True
	#temp
	LastID_M   = 100000
	LastID_S   = 200000
	LastID_E   = 300000
	LastID_MF  = 500000
	
	USE_INDEXES = False  	# Create indexes key/id
	AUTOCOMMIT  = False	# Only if database have a few record... 500?
				# It can be changed on runtime (to avoid commit during sync )
				
	MediaFilesCommited=True
	MoviesCommited   = True
	SeriesCommited   = True
	EpisodesCommited = True
	FailedCommited 	 = True
	
	ORDER_TITLE = 1
	ORDER_YEAR  = 2

	_dbMediaFiles	= None	# New table for other media.. or all in future...
	_dbMovies	= None
	_dbSeries	= None
	_dbEpisodes	= None	
	_dbFailed	= None

	_dbGroups	= None
	_dbGroupsItems	= None

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
	
	def loadAll (self):
		self._mediaFilesCheckLoaded()
		self._moviesCheckLoaded()
		self._seriesCheckLoaded()
#
#################################   MEDIAS   ################################# 
#
	def _loadMediaFilesDB(self):
		log("->", self, 10)
		if self._dbMediaFiles is None:
			start_time = time.time()
			self._dbMediaFiles = {}
			try:
				if os.path.exists(self.MEDIAFILESDB):
					fd = open(self.MEDIAFILESDB, "rb")
					self._dbMediaFiles = pickle.load(fd)
					fd.close()
					#self._upgradeMediaFiles(self._dbMediaFiles)
				else:
					self.setDBVersion(self._dbMediaFiles, self.DB_VERSION)
	
			except Exception, ex:
				print ex
				print '-'*60
				import sys, traceback
				traceback.print_exc(file=sys.stdout)
				print '-'*60
					
			elapsed_time = time.time() - start_time
			log("LoadMediaFiles Took : " + str(elapsed_time), self, 11)
					
			if self.USE_INDEXES:
				start_time = time.time()
				#self.createMediaFilesIndexes()
				elapsed_time = time.time() - start_time
				log("Indexing Took : " + str(elapsed_time), self, 11)

	def saveMediaFiles(self):		
		printl("->", self)
		if self.MediaFilesCommited:
			printl("Nothing to Commit", self)
			return
		start_time = time.time()
		try:		
			fd = open(self.MEDIAFILESDB, "wb")
			pickle.dump(self._dbMediaFiles, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			self.MoviesCommited = True
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)

	def _mediaFilesCheckLoaded(self):
		#log("->", self, 10)
		if self._dbMediaFiles is None:
			log("Media Files Not Loaded", self, 10)
			self._loadMediaFilesDB()
		
	## 
	# DML statements
	##
	def insertMediaWithDict(self, key_value_dict):
		log("->", self, 20)
		type = key_value_dict["MediaType"]
		
		m = MediaInfo()
		self.fillMediaInfo(m, key_value_dict)
				
		if type == MediaInfo.MOVIE:
			if not "ImdbId" in key_value_dict or key_value_dict['ImdbId'] == u"":
				log("ImdbId not defined", self, 5)
				return False		
			return self.insertMovie(m)		
		elif type == MediaInfo.SERIE:
			if not "TheTvDbId" in key_value_dict or key_value_dict['TheTvDbId'] == u"":
				log("TheTvDbId not defined", self, 5)
				return False		
			return self.insertSerie(m)
		elif type == MediaInfo.EPISODE:
			if not "TheTvDbId" in key_value_dict or key_value_dict['TheTvDbId'] == u"":
				log("TheTvDbId not defined", self, 5)
				return False		
			return self.insertEpisode(m)
			
		elif type == MediaInfo.MUSIC:
			self._mediaFilesCheckLoaded()
			self.LastID_MF+=1
			m.Id = self.LastID_MF
			key = m.Id
			m.Path = m.Path.replace("\\", "/")
			m.Path = m.Path.replace("//", "/")
			# Checks if the file is already in db
			if self.checkDuplicateMF(m.Path, m.Filename, m.Extension) is not None:
				printl("MediaFile Insert - Already exists", self)	
				#self._addFailedCauseOf = self._dbMediaFiles[key]
				return False
			
			if not key in self._dbMediaFiles:
				self.MediaFilesCommited = False
				self._dbMediaFiles[key] = m
				if self.AUTOCOMMIT:
					self.saveMediaFiles()
				return True	
			else: 
				self._addFailedCauseOf = self._dbMediaFiles[key]
				return False
			
			if self.AUTOCOMMIT:
				self.saveMediaFiles()
			return True			
		else:
			printl("MediaFile Insert - Type not specified", self)	
		
		return False	
	
	def updateMediaWithDict(self, key_value_dict):
		log("->", self, 20)
		if not "Id" in key_value_dict or key_value_dict['Id'] == u"":
				log("Id not defined", self, 5)
				return False
		type = int(key_value_dict['Id'])//100000
		
		if type == MediaInfo.MOVIE:
			if not "ImdbId" in key_value_dict or key_value_dict['ImdbId'] == u"":
				log("ImdbId not defined", self, 5)
				return False				
			self._moviesCheckLoaded()		
			m = self.getMovie(key_value_dict['Id'])
			if m is None:
				log("Media not found on DB [Id:"+ str(key_value_dict['Id']) +"]", self, 5)
				return False
		
			self.MoviesCommited = False
			self.fillMediaInfo(m, key_value_dict)	
			if self.AUTOCOMMIT:
				self.saveMovies()
			return True
		
		elif type == MediaInfo.SERIE:
			if not "TheTvDbId" in key_value_dict or key_value_dict['TheTvDbId'] == u"":
				log("TheTvDbId not defined", self, 5)
				return False			
			self._seriesCheckLoaded()
			m = self.getSerieWithId(key_value_dict['Id'])
			if m is None:
				log("Media not found on DB [Id:"+ str(key_value_dict['Id']) +"]", self, 5)
				return False
		
			self.SeriesCommited = False
			self.fillMediaInfo(m, key_value_dict)
			if self.AUTOCOMMIT:
				self.saveSeries()
			return True
		elif type == MediaInfo.EPISODE:
			if not "TheTvDbId" in key_value_dict or key_value_dict['TheTvDbId'] == u"":
				log("TheTvDbId not defined", self, 5)
				return False
			self._seriesCheckLoaded()
			m = self.getEpisodeWithId(key_value_dict['Id'])
			if m is None:
				log("Media not found on DB [Id:"+ str(key_value_dict['Id']) +"]", self, 5)
				return False
		
			self.EpisodesCommited = False
			self.fillMediaInfo(m, key_value_dict)
			if self.AUTOCOMMIT:
				self.saveEpisodes()
			return True
		
		elif type == MediaInfo.MUSIC:
			self._mediaFilesCheckLoaded()
			m = self.getMediaFileWithId(key_value_dict['Id'])
			if m is None:
				log("Media not found on DB [Id:"+ str(key_value_dict['Id']) +"]", self, 5)
				return False
		
			self.MediaFilesCommited = False
			self.fillMediaInfo(m, key_value_dict)
			if self.AUTOCOMMIT:
				self.saveMediaFiles()
			return True
			
		else:
			printl("MediaFile Update - Type not specified", self)	

		return False
			

	def deleteMedia(self, id):
		log("->", self, 20)
		type = int(id)//100000
		if type == MediaInfo.MOVIE:
			self._moviesCheckLoaded()
			key = self.getMovieKey(id)
			if key is not None:
				self.MoviesCommited = False
				del(self._dbMovies[key])	
				if self.AUTOCOMMIT:
					self.saveMovies()
				return True
			else:
				return False
		
		elif type == MediaInfo.SERIE:
			self._seriesCheckLoaded()
			key = self.getSerieKey(id)		
			if key is not None:

				if key in self._dbEpisodes:
					self.EpisodesCommited = False
					del(self._dbEpisodes[key])
				if key in self._dbSeries:	
					self.SeriesCommited = False
					del(self._dbSeries[key])
				if self.AUTOCOMMIT:
						self.saveEpisodes()
						self.saveSeries()
				return True
			else:
				return False
		
		elif type == MediaInfo.EPISODE:
			if not self.deleteEpisode(id):
				printl("Episode delete - DB Error", self)	
				return False
			else:
				return True
		
		elif type == MediaInfo.MUSIC:
			self._mediaFilesCheckLoaded()
			key = self.getMediaKey(id)
			if key is not None:
				self.MediaFilesCommited = False
				del(self._dbMediaFiles[key])	
				if self.AUTOCOMMIT:
					self.saveMediaFiles()
				return True
			else:
				return False
			
		else:
			printl("MediaFile Delete - Type not specified", self)	

		return False
		
	
	def deleteEpisode(self, id):
		log("-> id: " + str(id), self, 10)		
		if self.IDMODEAUTO:
			_id = int(id)
		else:
			_id = id
			
		self._seriesCheckLoaded()
		for serieKey in self._dbEpisodes:
			if serieKey != self.CONFIGKEY:
				for season in self._dbEpisodes[serieKey]:
					for episode in self._dbEpisodes[serieKey][season]:
						if self._dbEpisodes[serieKey][season][episode].Id == _id:	
							self.EpisodesCommited = False
							del(self._dbEpisodes[serieKey][season][episode])
							if len(self._dbEpisodes[serieKey][season]) == 0:
								del(self._dbEpisodes[serieKey][season])
							if len(self._dbEpisodes[serieKey]) == 0:
								del(self._dbEpisodes[serieKey])
								if serieKey in self._dbSeries:
									self.SeriesCommited = False
									del(self._dbSeries[serieKey])
							if self.AUTOCOMMIT:
								self.saveSeries()
								self.saveEpisodes()
							return True
		return False
	
	## 
	# SQL statements
	##
	def getMediaKey(self, id):
		log("->", self, 15)
		_id = int(id)
		
		self._mediaFilesCheckLoaded()
		start_time = time.time()
		k = None
		if self.USE_INDEXES:
			# use Indexes loaded at beginning
			# indexing 0.0007		
			#key = self.idxMoviesImdb[imdb]
			#element = self._dbMovies[key]			
			pass
		else:			
			# without indexing 0.02
			for key in self._dbMediaFiles:
				if key != self.CONFIGKEY:		# only for Pickle
					if self._dbMediaFiles[key].Id == _id:
						printl("result key: "+ str(key)+ "  for id:" + str(_id))
						k = key
						break
							
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return k

	def getMediaWithId(self, id):
		log("->  for id: "+str(id), self, 15)
		self._mediaFilesCheckLoaded()
		element = None
		key = self.getMediaKey(id)
		if key is not None:
			element = self._dbMediaFiles[key]
		
		return element
	# -------------------------------- PUBLIC -----------------------------
	def getMusics(self, order=None, firstRecord=0, numberOfRecords=9999999):
		log("->", self)
		list   = []
		listToReturn = []
		
		self._mediaFilesCheckLoaded()
		if self._dbMediaFiles is not None:
			start_time = time.time()
		
			for key in self._dbMediaFiles:
				if key != self.CONFIGKEY:
					if self._dbMediaFiles[key].Type == MediaInfo.MUSIC:
						list.append(self._dbMediaFiles[key])
			
			# sort by ....
			#if not sort is None: 			
			#	sortTable(list, sort)
			
			## return parcial listToReturn ---- (on Dict - orderdict only on 2.7)
			if firstRecord==0 and numberOfRecords==9999999:
				printl("All Records", self)
				listToReturn = list
			else:				
				recPosition = 0
				recCount = 0
				for item in list:
					if recPosition >= firstRecord:
						listToReturn.append(item)
						recCount += 1
					recPosition += 1
					if recCount >= numberOfRecords:
						break
			#printl("3 --------------------------------")
			#print (str(list))					

			elapsed_time = time.time() - start_time		
			printl("Took: " + str(elapsed_time), self)

		return listToReturn

	def getAlbuns(self, order=None, firstRecord=0, numberOfRecords=9999999):
		pass

	def getGenres(self, order=None, firstRecord=0, numberOfRecords=9999999):
		pass
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
			
			# Temporary to test ID's
			for movieKey in self._dbMovies:
				if movieKey != self.CONFIGKEY:
					if self.IDMODEAUTO:
						#key = int( str(time.time()) + str(random.randint(1000, 9999)) )
						#printl(str(key))
						self.LastID_M+=1
						self._dbMovies[movieKey].Id = self.LastID_M
					else:
						self._dbMovies[movieKey].Id = self._dbMovies[movieKey].ImdbId + str(random.randint(100, 999))


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

	# for test 
	def getDbDump(self):
		self._moviesCheckLoaded()
		self._seriesCheckLoaded()
		path = config.plugins.pvmc.tmpfolderpath.value + "/dumps"
		now = datetime.datetime.now()
		file = path + "/db_%04d%02d%02d_%02d%02d%02d.dump" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
		if not os.path.exists(path):
			os.makedirs(path)		
		f = open(file, "w")
		
		f.write("-- MediaFiles - Movies --\n")
		f.write("\n")
		f.write("Count\tKey\t\tId\tParent\tTitle\n")		
		f.write("\n")
		cnt=0
		s = u""
		for key in self._dbMovies:
			cnt += 1
			s = str(cnt) + "\t"			
			if key == self.CONFIGKEY:		
				s += str(key) + "\t"
				s += "Version " + str(self._dbMovies[key])
				s += "\n"
			else:
				s += str(key) + "\t"
				s += str(self._dbMovies[key].Id) + "\t"
				s += str(self._dbMovies[key].ParentId) + "\t"
				s += str(self._dbMovies[key].Title) + "\t"
			f.write(s+"\n")

		f.write("\n")
		f.write("-- MediaFiles - Series --\n")
		f.write("\n")
		f.flush()

		cnt=0
		for key in self._dbSeries:
			cnt += 1
			s = str(cnt) + "\t"			
			s += str(key) + "\t"
			if key == self.CONFIGKEY:		
				s += "Version " + str(self._dbSeries[key])
				s += "\n"
			else:
				s += str(self._dbSeries[key].Id) + "\t"
				s += str(self._dbSeries[key].ParentId) + "\t"
				s += str(self._dbSeries[key].Title) + "\t"
			f.write(s+"\n")
			
		f.write("\n")
		f.write("-- Episodes --\n")
		f.write("\n")
		f.write("Count\tKey\tKey2\tKey3\tId\tParent\tTitle\n")		
		f.write("\n")
		f.flush()
		
		cnt=0
		for key in self._dbEpisodes:
			if key == self.CONFIGKEY:		
				s += "Version " + str(self._dbEpisodes[key])
				s += "\n"
			else:
				for season in self._dbEpisodes[key]:
					for episode in self._dbEpisodes[key][season]:
						cnt += 1
						s = str(cnt) + "\t"		
						s += str(key) + "\t"
						s += str(season) + "\t"
						s += str(episode) + "\t"
						s += str(self._dbEpisodes[key][season][episode].Id) + "\t"
						s += str(self._dbEpisodes[key][season][episode].ParentId) + "\t"
						s += str(self._dbEpisodes[key][season][episode].Title) + "\t"
						f.write(s+"\n")

		f.write("\n")
		f.flush()
		
		return True		

	#used on deleteMissingFiles
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
		
	def getMovieKey(self, id):
		log("->", self, 15)
		if self.IDMODEAUTO:
			_id = int(id)
		else:
			_id = id

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
			for key in self._dbMovies:
				if key != self.CONFIGKEY:		# only for Pickle
					if self._dbMovies[key].Id == _id:
						k = key
						break
							
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return key

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
			for movieKey in self._dbMovies:
				if movieKey != self.CONFIGKEY:		# only for Pickle
					if self._dbMovies[movieKey].ImdbId == imdbId:
						key = movieKey
						break
		
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return key

	def getMovie(self, id):
		log("->", self, 15)
		self._moviesCheckLoaded()
		element = None
		key = self.getMovieKey(id)
		if key is not None:
			element = self._dbMovies[key]
						
		return element

	## 
	# DML statements
	##
	def insertMovie(self, media):
		log("->", self, 20)
		self._moviesCheckLoaded()
		m = media
		if self.IDMODEAUTO:
			self.LastID_M+=1
			m.Id = self.LastID_M
		else:
			m.Id = m.ImdbId + str(random.randint(100, 999))
		m.setMediaType(MediaInfo.MOVIE)
		m.Path = media.Path.replace("\\", "/")
		m.Path = media.Path.replace("//", "/")
		movieKey = m.ImdbId
		#movieKey = media.Id
		# Checks if the file is already in db
		if self.checkDuplicate(media.Path, media.Filename, media.Extension) is not None:
			# This should never happen, this means that the same file is already in the db
			printl("Movie Insert - Already exists", self)	
			self._addFailedCauseOf = self._dbMovies[movieKey]
			return False
		
		if not movieKey in self._dbMovies:
			self.MoviesCommited = False
			self._dbMovies[movieKey] = m
			if self.AUTOCOMMIT:
				self.saveMovies()
			return True	
		else: 
			self._addFailedCauseOf = self._dbMovies[movieKey]
			return False
		
		if self.AUTOCOMMIT:
			self.saveMovies()
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
		
			# Temporary to test ID's
			for key in records:
				if key != self.CONFIGKEY:
					if self.IDMODEAUTO:
						self.LastID_S+=1
						records[key].Id = self.LastID_S
					else:
						records[key].Id = records[key].TheTvDbId
			
				
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
			
			# Temporary to test ID's
			for serieKey in records:
				if serieKey != self.CONFIGKEY:
					for season in records[serieKey]:
						for episode in records[serieKey][season]:
							if self.IDMODEAUTO:
								self.LastID_E+=1
								records[serieKey][season][episode].Id = self.LastID_E
							else:
								records[serieKey][season][episode].Id = str(serieKey) + str(season) + str(episode) + str(random.randint(100, 999))
							records[serieKey][season][episode].ParentId = self._dbSeries[serieKey].Id;

		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60

		return (records)
		
	#Call when data is needed, to verify if is loaded
	def _seriesCheckLoaded(self):
		#log("->", self, 15)
		if self._dbSeries is None:
			self._loadSeriesEpisodesDB()

	#								    #	
	#   PUBLIC FUNCTIONS	# # # # # # # # # # # # # # # # # # # # # # # 
	#								    #	
#	def saveSeries(self):		
	#def getSeries(self, order=None, firstRecord=0, numberOfRecords=9999999):
	#def getSeriesCount(self):
	

#	def insertSerie(self, media):
#	def insertSerieWithDict(self, key_value_dict):
#	def updateSerieWithDict(self, key_value_dict):		#ID is Required
#	def deleteSerie(self, id):
	
	
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
		
	#used on transformgenres
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
		
	#def getSeriesCountSeasonsWithKey(self, serieKey):
	#	log("->", self, 15)
	#	self._seriesCheckLoaded()
	#	count = None
	#	if serieKey in self._dbEpisodes:
	#		count = len(self._dbEpisodes[serieKey])
	#	return count
	#
	
	def getSerieKey(self, id):
		log("->", self, 15)
		if self.IDMODEAUTO:
			_id = int(id)
		else:
			_id = id

		self._seriesCheckLoaded()
		start_time = time.time()
		k = None
		if self.USE_INDEXES:
			# use Indexes loaded at beginning
			# indexing 0.0007		
			#key = self.idxMoviesImdb[imdb]
			#element = self._dbMovies[key]			
			pass
		else:			
			# without indexing 0.02
			for key in self._dbSeries:
				if key != self.CONFIGKEY:		# only for Pickle
					if self._dbSeries[key].Id == _id:
						printl("result key: "+ str(key)+ "  for id:" + str(_id))
						k = key
						break
							
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return k

	def getSeriesIdWithTheTvDbId(self, theTvDbId):
		log("->", self, 15)
		self._seriesCheckLoaded()
		start_time = time.time()
		id = None
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
						id = self._dbSeries[serieKey].Id
						break
		
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return id

	def getSerieWithId(self, id):
		log("->  for id: "+str(id), self, 15)
		self._seriesCheckLoaded()
		element = None
		key = self.getSerieKey(id)
		if key is not None:
			element = self._dbSeries[key]
		
		return element
		
	#
	#def getSerieSeasons(self, serieKey):
	#	log("->", self, 15)
	#	self._seriesCheckLoaded()
	#	if serieKey in self._dbEpisodes:
	#		return self._dbEpisodes[serieKey].keys()
	#			
	#	return self.seriesGetAll().values()

	def insertSerie(self, media):
		log("->", self, 20)
		self._seriesCheckLoaded()
		m = media
		if self.IDMODEAUTO:
			self.LastID_S+=1
			m.Id = self.LastID_S
		else:
			m.Id = m.TheTvDbId + str(random.randint(100, 999))
		serieKey = m.TheTvDbId
		#serieKey = media.Id
		m.Path = media.Path.replace("\\", "/")
		m.Path = media.Path.replace("//", "/")
		# Checks if the file is already in db
		if self.checkDuplicate(media.Path, media.Filename, media.Extension) is not None:
			# This should never happen, this means that the same file is already in the db
			printl("Serie Insert - Already exists", self)	
			return False
		
		if not serieKey in self._dbSeries:
			self.SeriesCommited = False
			self._dbSeries[serieKey] = m
			if self.AUTOCOMMIT:
				self.saveSeries()
			return True	
		else: 
			self._addFailedCauseOf = self._dbSeries[serieKey]
			return False
		
		if self.AUTOCOMMIT:
			self.saveSeries()
		return True
	
#	
################################   EPISODES   ################################ 
#
#	def saveEpisodes(self):		
#
#	def getEpisodes(self, id=None, season=None):
#	def getEpisodeWithId(self, id):
#	def insertEpisode(self, media):
#	def insertEpisodeWithDict(self, key_value_dict):
#	def updateEpisodeWithDict(self, key_value_dict):		#ID is Required
#	def deleteEpisode(self, id):
	
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
	
	def getEpisodes(self, mediaId=None, season=None):
		log("-> id:"+ str(mediaId) + " season:" + str(season), self, 15)
		self._seriesCheckLoaded()
		list = []
		if mediaId is None:
			for key in self._dbEpisodes:
				if key != self.CONFIGKEY:
					for season in self._dbEpisodes[key]:
						for episode in self._dbEpisodes[key][season]:
							list.append(self._dbEpisodes[key][season][episode])
		elif season is None:
			for key in self._dbEpisodes:
				if key != self.CONFIGKEY:
					for season in self._dbEpisodes[key]:
						for episode in self._dbEpisodes[key][season]:
							#printl("Parentid: " + str(self._dbEpisodes[key][season][episode].ParentId) +" Request: " + str(mediaId) );
							if self.IDMODEAUTO:
								if self._dbEpisodes[key][season][episode].ParentId == int(mediaId):
									#printl("id:" + str(self._dbEpisodes[key][season][episode].Id)  +" parentid: " + str(self._dbEpisodes[key][season][episode].ParentId) +" Request: " + str(mediaId) );
									list.append(self._dbEpisodes[key][season][episode])
							else:
								if self._dbEpisodes[key][season][episode].ParentId == mediaId:
									list.append(self._dbEpisodes[key][season][episode])
		else:				
			for key in self._dbEpisodes:
				if key != self.CONFIGKEY:
					for season in self._dbEpisodes[key]:
						for episode in self._dbEpisodes[key][season]:
							if self._dbEpisodes[key][season][episode].ParentId == mediaId:
								if self._dbEpisodes[key][season][episode].Season == season:
									list.append(self._dbEpisodes[key][season][episode])
		return list
		
	def getEpisodesWithKey(self, serieKey=None, season=None):
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


	def getEpisodeWithId(self, id):
		log("->", self, 10)
		if self.IDMODEAUTO:
			_id = int(id)
		else:
			_id = id
		self._seriesCheckLoaded()
		for serieKey in self._dbEpisodes:
			if serieKey != self.CONFIGKEY:
				for season in self._dbEpisodes[serieKey]:
					for episode in self._dbEpisodes[serieKey][season]:
						if self._dbEpisodes[serieKey][season][episode].Id == _id:	
							return self._dbEpisodes[serieKey][season][episode]
								
		return None

	def insertEpisode(self, media):
		log("->", self, 20)
		self._seriesCheckLoaded()
		m = media
		#printl("inserting id: " +str(m.Id)+" parentid: " +str(m.ParentId) + " in: " +str(m.Path+ m.Filename+ m.Extension) )
		if self.IDMODEAUTO:
			self.LastID_E+=1
			m.Id = self.LastID_E
		else:
			m.Id = str(m.TheTvDbId) + str(m.Season) + str(m.Episode) + str(random.randint(100, 999))
		serieKey = m.TheTvDbId
		if m.ParentId is None:	# from Sync
			m.ParentId = self.getSeriesIdWithTheTvDbId(m.TheTvDbId)
			
		#serieKey = media.Id
		m.setMediaType(MediaInfo.EPISODE)
		m.Path = media.Path.replace("\\", "/")
		m.Path = media.Path.replace("//", "/")
		
		#printl("inserting id: " +str(m.Id)+" parentid: " +str(m.ParentId) + " in: " +str(m.Path+ media.Filename+ media.Extension) )
				
		# Checks if the file is already in db
		if self.checkDuplicate(media.Path, media.Filename, media.Extension) is not None:
			# This should never happen, this means that the same file is already in the db
			printl("Episode Insert - Already exists", self)	
			return False
		
		self.EpisodesCommited = False
		if not serieKey in self._dbEpisodes:
			self._dbEpisodes[serieKey] = {}
		
		if not m.Season in self._dbEpisodes[serieKey]:
			self._dbEpisodes[serieKey][m.Season] = {}
		
		if not m.Episode in self._dbEpisodes[serieKey][m.Season]:
			self._dbEpisodes[serieKey][m.Season][m.Episode] = m			
			printl("inserted on _dbEpisodes: " +str(serieKey)+" : " +str(m.Season) + " : " +str(m.Episode) + " - ParentID:" +str(m.ParentId) )
		else:
			self._addFailedCauseOf = self._dbEpisodes[serieKey][m.Season][m.Episode]
			return False
		
		if self.AUTOCOMMIT:
			self.saveEpisodes()
		return True

	def getEpisodesCount(self, mediaId=None, season=None):
		log("->", self, 15)
		self._seriesCheckLoaded()
		list = self.getEpisodes(mediaId, season)
		return len(list)
		
		
#	
#################################   FAILED   ################################# 
#
	def _loadFailedDB(self):
		#printl("->", self)
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
		#log("->", self, 10)
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

	def fillMediaInfo(self, m, key_value_dict):
		intFields = ['Year', 'Month', 'Day', 'Runtime', 'Popularity', 'Season', 'Episode']
		if self.IDMODEAUTO:
			intFields.append("Id")
			intFields.append("ParentId")
		
		for key in key_value_dict.keys():
			try:
				if key in intFields:
					if key_value_dict[key] is None or key_value_dict[key] == "": # To avoid null Values
						value = None
					else:
						value = int(key_value_dict[key])
				else:
					value = key_value_dict[key]
				
				setattr(m, key, value)

			except Exception, ex:
				log("Key error: "+ str(key) + " Ex: " + str(ex), self, 5)

	def checkDuplicateMF(self, path, filename, extension):
		self._mediaFilesCheckLoaded()
		#self._mediaEpisodesCheckLoaded()
		
		if self._dbMediaFiles is not None:
			for key in self._dbMediaFiles:
				if key == self.CONFIGKEY:		# only for Pickle
					continue
				if self._dbMediaFiles[key].Path == path:
					if self._dbMediaFiles[key].Filename == filename:
						if self._dbMediaFiles[key].Extension == extension:
							return self._dbMediaFiles[key]
		return None
	
	def checkDuplicate(self, path, filename, extension):
		self._moviesCheckLoaded()
		self._seriesCheckLoaded()
		self._failedCheckLoaded()

		if self._dbMovies is not None:
			for key in self._dbMovies:
				if key == self.CONFIGKEY:		# only for Pickle
					continue
				if self._dbMovies[key].Path == path:
					if self._dbMovies[key].Filename == filename:
						if self._dbMovies[key].Extension == extension:
							return self._dbMovies[key]

		if self._dbSeries is not None:
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

