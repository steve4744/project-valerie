# -*- coding: utf-8 -*-

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

#------------------------------------------------------------------------------------------

gDatabase = None
gDatabaseMutex = Lock()

class Database(object):
	FAILEDDB = config.plugins.pvmc.configfolderpath.value + "failed.db"

	MOVIESDB   = config.plugins.pvmc.configfolderpath.value + "movies.db"
	TVSHOWSDB  = config.plugins.pvmc.configfolderpath.value + "tvshows.db"
	EPISODESDB = config.plugins.pvmc.configfolderpath.value + "episodes.db"

	MOVIESTXD  = config.plugins.pvmc.configfolderpath.value + "movies.txd"
	TVSHOWSTXD = config.plugins.pvmc.configfolderpath.value + "tvshows.txd"
	
	DB_NONE = 0
	DB_TXD = 2
	DB_PICKLE = 3
	DB_SQLITE= 4

	USE_DB_TYPE    = DB_NONE
	
	TXD_VERSION = 3
	
	# New Const's
	DB_PATH           = config.plugins.pvmc.configfolderpath.value
	DB_PATH_EPISODES  = config.plugins.pvmc.configfolderpath.value + "episodes/"
	DB_TXD_FILENAME_M = "movies.txd"
	DB_TXD_FILENAME_S = "tvshows.txd"

	def __init__(self):
		printl("", self)
		#self.db = databaseHandler().getInstance()
		
		#if self.db.DB_SQLITE_LOADED:
		#	self.setDBType(self.DB_SQLITE)
		
		#el
		
		# Deactivate usage of txd files
		#if os.path.exists(self.DB_PATH + self.DB_TXD_FILENAME_M):
		#	self.setDBType(self.DB_TXD)
		#
		#elif os.path.exists(self.DB_PATH + self.DB_TXT_FILENAME_M):
		#	self.setDBType(self.DB_TXT)
			#self.setDBVersion(DB_TXD)
		# No exception if exists movies.txd and no tvshows.txd

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
			if self.dbMovies.has_key(media.ImdbId) is True:
				del(self.dbMovies[media.ImdbId])
				return True
		if media.isSerie or isSerie:
			if self.dbSeries.has_key(media.TheTvDbId) is True:
				del(self.dbSeries[media.TheTvDbId])
				return True
		if media.isEpisode or isEpisode:
			if self.dbEpisodes.has_key(media.TheTvDbId) is True:
				if self.dbEpisodes[media.TheTvDbId].has_key(media.Season) is True:
					if self.dbEpisodes[media.TheTvDbId][media.Season].has_key(media.Episode) is True:
						del(self.dbEpisodes[media.TheTvDbId][media.Season][media.Episode])
						if len(self.dbEpisodes[media.TheTvDbId][media.Season]) == 0:
							del(self.dbEpisodes[media.TheTvDbId][media.Season])
						if len(self.dbEpisodes[media.TheTvDbId]) == 0:
							del(self.dbEpisodes[media.TheTvDbId])
							if self.dbSeries.has_key(media.TheTvDbId) is True:
								del(self.dbSeries[media.TheTvDbId])
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
			if self.dbSeries.has_key(media.TheTvDbId) is False:
				self.dbSeries[media.TheTvDbId] = media
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
			if self.dbMovies.has_key(media.ImdbId) is False:
				self.dbMovies[media.ImdbId] = media
			else: 
				self._addFailedCauseOf = self.dbMovies[media.ImdbId]
				return False
		elif media.isEpisode:
			if self.dbEpisodes.has_key(media.TheTvDbId) is False:
				self.dbEpisodes[media.TheTvDbId] = {}
			
			if self.dbEpisodes[media.TheTvDbId].has_key(media.Season) is False:
				self.dbEpisodes[media.TheTvDbId][media.Season] = {}
			
			if self.dbEpisodes[media.TheTvDbId][media.Season].has_key(media.Episode) is False:
				self.dbEpisodes[media.TheTvDbId][media.Season][media.Episode] = media
			else:
				self._addFailedCauseOf = self.dbEpisodes[media.TheTvDbId][media.Season][media.Episode]
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
		#if self.USE_DB_TYPE == self.DB_PICKLE:
		self.savePickel()
		
		if self.USE_DB_TYPE == self.DB_TXD:
			self.saveTxd()
		elif self.USE_DB_TYPE == self.DB_SQLITE:
			self.saveSql()
		gDatabaseMutex.release()

	def saveTxd(self):
		start_time = time.time()	
		f = Utf8.Utf8(self.MOVIESTXD, 'w')
		f.write(unicode(self.TXD_VERSION) + u"\n")
		for movie in self.dbMovies.values():
			f.write(movie.exportDefined(self.TXD_VERSION))
		f.write("EOF\n")
		f.close()
		elapsed_time = time.time() - start_time
		printl("Took (movies.txd): " + str(elapsed_time), self)
		
		start_time = time.time()	
		f = Utf8.Utf8(self.TVSHOWSTXD, 'w')
		f.write(unicode(self.TXD_VERSION) + u"\n")
		for key in self.dbSeries:
			if self.dbEpisodes.has_key(key): # Check if we have episodes for that serie
				f.write(self.dbSeries[key].exportDefined(self.TXD_VERSION))
		f.write("EOF\n")
		f.close()
		elapsed_time = time.time() - start_time
		printl("Took (tvshows.txd): " + str(elapsed_time), self)
		
		start_time = time.time()  
		for serie in self.dbEpisodes:
			try:
				f = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + u"episodes/" + serie + u".txd", 'w')
				f.write(unicode(self.TXD_VERSION) + u"\n")
				for season in self.dbEpisodes[serie]:
					for episode in self.dbEpisodes[serie][season].values():
						f.write(episode.exportDefined(self.TXD_VERSION))
				f.write("EOF\n")
				f.close()
			except Exception, ex: 
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		elapsed_time = time.time() - start_time
		printl("Took (episodes/*.txd): " + str(elapsed_time), self)

	def savePickel(self):
		start_time = time.time()  
		fd = open(self.FAILEDDB, "wb")
		pickle.dump(self.dbFailed, fd, pickle.HIGHEST_PROTOCOL)
		fd.close()
		elapsed_time = time.time() - start_time
		printl("Took (failed.db): " + str(elapsed_time), self)
		
		start_time = time.time()  
		fd = open(self.MOVIESDB, "wb")
		pickle.dump(self.dbMovies, fd, pickle.HIGHEST_PROTOCOL)
		fd.close()
		elapsed_time = time.time() - start_time
		printl("Took (movies.db): " + str(elapsed_time), self)
		
		
		#dbMovies2 = []
		#for movie in self.dbMovies.values():
		#	#print movie
		#	from struct.Media import MediaMovie
		#	m = MediaMovie()
		#	m.Path         = movie.Path
		#	m.Filename     = movie.Filename
		#	m.Extension    = movie.Extension
		#	m.Title        = movie.Title
		#	m.AiredYear    = movie.Year
		#	m.AiredMonth   = movie.Month
		#	m.AiredDay     = movie.Day
		#	m.CreatedYear  = 0
		#	m.CreatedMonth = 0
		#	m.CreatedDay   = 0
		#	m.Runtime      = movie.Runtime
		#	
		#	m.ImdbId       = movie.ImdbId
		#	m.TmDbId       = movie.TmDbId
		#	m.Tag          = movie.Tag
		#	m.Popularity   = movie.Popularity
		#	m.Resolution   = movie.Resolution
		#	m.Sound        = movie.Sound
		#	dbMovies2.append(m)
		#
		#start_time = time.time()  
		#fd = open(self.MOVIESDB+"2", "wb")
		#pickle.dump(dbMovies2, fd, pickle.HIGHEST_PROTOCOL)
		#fd.close()
		#elapsed_time = time.time() - start_time
		#printl("Took (movies.db): " + str(elapsed_time), self)
		
		start_time = time.time()  
		fd = open(self.TVSHOWSDB, "wb")
		pickle.dump(self.dbSeries, fd, pickle.HIGHEST_PROTOCOL)
		fd.close()
		elapsed_time = time.time() - start_time
		printl("Took (tvshows.db): " + str(elapsed_time), self)
		
		#start_time = time.time()
		#for serie in self.dbEpisodes:
		#	fd = open(config.plugins.pvmc.configfolderpath.value + u"episodes/" + serie + u".db", "wb")
		#	pickle.dump(self.dbEpisodes[serie], fd, pickle.HIGHEST_PROTOCOL)
		#	fd.close()
		#elapsed_time = time.time() - start_time
		#print "Took (episodes/*.db): ", elapsed_time
		
		start_time = time.time()
		fd = open(self.EPISODESDB, "wb")
		pickle.dump(self.dbEpisodes, fd, pickle.HIGHEST_PROTOCOL)
		fd.close()
		elapsed_time = time.time() - start_time
		printl("Took (episodes.db): " + str(elapsed_time), self)

	def saveSql(self):
		# for moviesdb
		#	insert on media
		# for seriesdb
		#	insert on media
		#	insert on episodes
		#
		start_time = time.time()
		
		#
		#  Code Removed to avoid version problems 
		#
		
		elapsed_time = time.time() - start_time
		printl("Took (SQL): " + str(elapsed_time), self)

	def _load(self):
		if len(self.dbFailed) == 0 and os.path.isfile(self.FAILEDDB):
			fd = open(self.FAILEDDB, "rb")
			self.dbFailed = pickle.load(fd)
			fd.close()
		
		if len(self.dbMovies) == 0:
			try:
				if os.path.isfile(self.MOVIESDB):
					self.loadPickle(True, False) 
				elif os.path.isfile(self.MOVIESTXD):
					self.loadTxd(True, False) 
			except Exception, ex:
				printl("Loading movie db failed! Ex: " + str(ex), __name__, "E")
		
		if len(self.dbSeries) == 0 or len(self.dbEpisodes) == 0:
			try:
				if os.path.isfile(self.TVSHOWSDB) and os.path.isfile(self.EPISODESDB):
					self.loadPickle(False, True) 
				elif os.path.isfile(self.TVSHOWSTXD):
					self.loadTxd(False, True) 
			except Exception, ex:
				printl("Loading tv db failed! Ex: " + str(ex), __name__, "E")
		
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

	def loadTxd(self, loadMovie, loadTVShow):
		if loadMovie:
			start_time = time.time()
			try:
				db = Utf8.Utf8(self.MOVIESTXD, "r").read()
				if db is not None:
					lines = db.split("\n")
					version = int(lines[0])
					linesLen = len(lines)
					
					size = 11
					if version >= 3:
						size = 13
					else:
						size = 11
					
					for i in range(1, linesLen, size):
						if lines[i] == "EOF":
							break
						m = MediaInfo()
						m.importDefined(lines[i:i+size], version, True, False, False)
						self.add(m)
			except Exception, ex:
				print ex
				print '-'*60
				import sys, traceback
				traceback.print_exc(file=sys.stdout)
				print '-'*60
			
			elapsed_time = time.time() - start_time
			printl("Took (movies.txd): " + str(elapsed_time), self)
		
		if loadTVShow:
			start_time = time.time()
			try:
				db = Utf8.Utf8(self.TVSHOWSTXD, "r").read()
				if db is not None:
					lines = db.split("\n")
					version = int(lines[0])
					linesLen = len(lines)
					
					size = 9
					if version >= 3:
						size = 11
					else:
						size = 9
					
					for i in range(1, linesLen, size):
						if lines[i] == "EOF":
							break
						m = MediaInfo()
						m.importDefined(lines[i:i+size], version, False, True, False)
						self.add(m)
			except Exception, ex:
				print ex
				print '-'*60
				import sys, traceback
				traceback.print_exc(file=sys.stdout)
				print '-'*60
			
			elapsed_time = time.time() - start_time
			printl("Took (tvshows.txd): " + str(elapsed_time), self)
			
			start_time = time.time()
			try:	
				for key in self.dbSeries:
					db = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + u"episodes/" + key + u".txd", "r").read()
					if db is not None:
						lines = db.split("\n")
						version = int(lines[0])
						linesLen = len(lines)
						
						size = 12
						if version >= 3:
							size = 14
						else:
							size = 12
						
						for i in range(1, linesLen, size):
							if lines[i] == "EOF":
								break
							m = MediaInfo()
							m.importDefined(lines[i:i+size], version, False, False, True)
							self.add(m)
			except Exception, ex:
				print ex
				print '-'*60
				import sys, traceback
				traceback.print_exc(file=sys.stdout)
				print '-'*60
			elapsed_time = time.time() - start_time
			printl("Took (episodes/*.txd): " + str(elapsed_time), self)

	def loadPickle(self, loadMovie, loadTVShow):
		if loadMovie:
			try:
				start_time = time.time()
				fd = open(self.MOVIESDB, "rb")
				self.dbMovies = pickle.load(fd)
				fd.close()
				elapsed_time = time.time() - start_time
				printl("Took (movies.db): " + str(elapsed_time), self)
			except Exception, ex:
				printl("Exception: " + str(ex), self)
		
		if loadTVShow:
			try:
				start_time = time.time()
				fd = open(self.TVSHOWSDB, "rb")
				self.dbSeries = pickle.load(fd)
				fd.close()
				elapsed_time = time.time() - start_time
				printl("Took (tvshows.db): " + str(elapsed_time), self)
			except Exception, ex:
				printl("Exception: " + str(ex), self)
			
			#start_time = time.time()
			#self.dbEpisodes = {}
			#for key in self.dbSeries:
			#	episode = {}
			#	fd = open(config.plugins.pvmc.configfolderpath.value + u"episodes/" + key + u".db", "wb")
			#	self.dbEpisodes[key] = pickle.load(fd)
			#	fd.close()
			#elapsed_time = time.time() - start_time
			#print "Took (episodes/*.db): ", elapsed_time
			
			try:
				start_time = time.time()
				self.dbEpisodes = {}
				fd = open(self.EPISODESDB, "rb")
				self.dbEpisodes = pickle.load(fd)
				fd.close()
				elapsed_time = time.time() - start_time
				printl("Took (episodes.db): " + str(elapsed_time), self)
			except Exception, ex:
				printl("Exception: " + str(ex), self)
