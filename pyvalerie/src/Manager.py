# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   Manager.py
#   Project Valerie - Layer between user interfaces and background processing
#
#   Created by user on 00/00/0000.
#   Manager
#   
#   Revisions:
#   v1 - 15/07/2011 - Zuki - Avoid null values on Dates, Popularity & Runtime
#
#   v2 - 18/07/2011 - Zuki - Added Counters for Movies/Series
#
#   v
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import Blacklist
import Config
from   PVS_DatabaseHandler import Database
from   MediaInfo import MediaInfo
from   MobileImdbComProvider import MobileImdbComProvider
import replace
from   sync import Sync
from Arts import Arts

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__common__ import log as log

import os

class Manager():

	MOVIES = 0
	TVSHOWS = 1
	TVSHOWSSEASONS = 5
	TVSHOWSEPISODES = 2
	FAILED = 3
	FAILED_ALL = 4
	
	ORDER_TITLE = 1
	ORDER_YEAR  = 2

	def __init__(self):
		printl("->", self)
		try:
			Config.load()
			self.db = Database().getInstance()
			replace.load()
		except Exception, ex:
			printl ("Exception on Init Ex:"+str(ex), self)
			from Plugins.Extensions.ProjectValerieSync.sync import checkDefaults
			checkDefaults()
			
			Config.load()
			self.db = Database().getInstance()
			replace.load()

	def finish(self):
		printl("", self)
		self.db.save()

	def reload(self):
		printl("", self)
		self.db.reload()

	def getAll(self, type, param=None):
		printl("type=" + str(type) + " param=" + str(param), self)
					
		if type == self.MOVIES:
			return self.db.getMoviesValues()
					
		elif type == self.TVSHOWS:
			return self.db.getSeriesValues()
			
		elif type == self.TVSHOWSEPISODES:
			list = []
			if param is not None:
				list = self.db.getSeriesEpisodesWithTheTvDbId(param)
			else:
				list = self.db.getSeriesEpisodesValues()
			return list
		
		elif type == self.TVSHOWSSEASONS: 
			#getAll(Manager.TVSHOWSSEASONS, (thetvdbid, )
			if param is not None and len(param) == 1:
				list = self.db.getSeriesSeasons(param[0])

			#getAll(Manager.TVSHOWSSEASONS, (thetvdbid, season, )
			elif param is not None and len(param) == 2:
				serie  = param[0]
				season = param[1]
				list = self.db.getSeriesEpisodes(serie, season)
			
			return list
		
		elif type == self.FAILED or type == self.FAILED_ALL:
			return self.db.getFailed()
		else:
			return None

	def searchAlternatives(self, oldElement, searchstring=None):
		element = MediaInfo(oldElement.Path, oldElement.Filename, oldElement.Extension)
		if type(oldElement) is MediaInfo:
			element.isMovie = oldElement.isMovie
			element.isSerie = oldElement.isSerie
		
		if searchstring is not None:
			element.SearchString = searchstring
			
		element.parse()
		
		printl("SEARCH=" + str(element.SearchString), self)
		return MobileImdbComProvider().getAlternatives(element)

	def syncElement(self, path, filename, extension, imdbid, istvshow, oldelement=None):
		printl(str(path) + " " + str(filename) + " " + str(extension) + " " + str(imdbid) + " " + str(istvshow), self)
		
		element = None
		
		if oldelement is None:
			element = MediaInfo(path, filename, extension)
			element.parse()
			element.ImdbId = imdbid
		else:
			element = oldelement.copy()
		
		if istvshow:
			element.setMediaType(MediaInfo.SERIE)
		else:
			element.setMediaType(MediaInfo.MOVIE)
		
		results = Sync().syncWithId(element)
		if results is not None:
			return results
		else:
			if istvshow is False:
				element.setMediaType(MediaInfo.SERIE)
			else:
				element.setMediaType(MediaInfo.MOVIE)
			
			results = Sync().syncWithId(element)
			if results is not None:
				return results
		return None

	def replace(self, oldElement, newElement):
		printl("", self)
		# not consistent ...todo: update serie
		if oldElement is not None:
			printl("oldElement=" + str(oldElement), self)
			if type(oldElement) is MediaInfo:
				printl("RM " + str(self.db.remove(oldElement)), self)
			else:
				self.db.removeFailed(oldElement)
		
		if newElement is not None:
			if len(newElement) == 2:
				printl("newElement=" + str(newElement[0]), self)
				printl("ADD " + str(self.db.add(newElement[0])), self)
				printl("newElement=" + str(newElement[1]), self)
				printl("ADD " + str(self.db.add(newElement[1])), self)
			else:
				printl("newElement=" + str(newElement[0]), self)
				printl("ADD " + str(self.db.add(newElement[0])), self)

	def remove(self, oldElement, blacklist=True):
		printl("", self)
		if oldElement is not None:
			printl("oldElement=" + str(oldElement), self)
			if type(oldElement) is MediaInfo:
				b = self.db.remove(oldElement)
				printl("RM " + str(b), self)
				if b and blacklist:
					Blacklist.add(oldElement.Filename + u"." + oldElement.Extension)
					Blacklist.save()
			else:
				self.db.removeFailed(oldElement)
				Blacklist.add(oldElement.Filename + u"." + oldElement.Extension)
				Blacklist.save()

	def getElementByUsingPrimaryKey(self, type, primary_key):
		printl("", self)
		printl("type=" + str(type), self)
		printl("primary_key=" + str(primary_key), self)
		element = None
		if type == self.MOVIES and primary_key.has_key("imdbid"):
			printl("is_Movie found", self)
			imdbid = primary_key["imdbid"]
			element = self.db.getMoviesWithKey(imdbid)
		
		elif type == self.TVSHOWS and primary_key.has_key("thetvdbid"):
			printl("is_TvShow found", self)
			thetvdbid = primary_key["thetvdbid"]
			element = self.db.getSeriesWithKey(thetvdbid)
		
		elif type == self.TVSHOWSEPISODES and primary_key.has_key("thetvdbid") and primary_key.has_key("season") and primary_key.has_key("episode"):
			printl("is_Episode found", self)
			thetvdbid = primary_key["thetvdbid"]
			season = int(primary_key["season"])
			episode = int(primary_key["episode"])
			printl("Looking up episode", self, "D")
			#print self.db._dbEpisodes.has_key(thetvdbid)
			#print self.db._dbEpisodes[thetvdbid]
			#print self.db._dbEpisodes[thetvdbid].has_key(season)
			#print self.db._dbEpisodes[thetvdbid][season].has_key(episode)
			element = self.db.getSeriesEpisode(thetvdbid, season, episode)
		
		return element

	def removeByUsingPrimaryKey(self, type, primary_key):
		printl("", self)
		printl("type=" + str(type), self)
		printl("primary_key=" + str(primary_key), self)
		element = self.getElementByUsingPrimaryKey(type, primary_key)
		if element is not None:
			self.remove(element, False)
			return True
		return False

	def fillElement(self, newElement, key_value_dict):
		printl("", self)
		for key in key_value_dict.keys():
			if key == "Title":
				newElement.Title = key_value_dict[key]
			elif key == "Year":
				if key_value_dict[key] is None or key_value_dict[key] == "": # To avoid null Values
					value = None
				else:
					value = int(key_value_dict[key])
				newElement.Year = value
			elif key == "Month":
				if key_value_dict[key] is None or key_value_dict[key] == "": # To avoid null Values
					value = None
				else:
					value = int(key_value_dict[key])
				newElement.Month = value
			elif key == "Day":
				if key_value_dict[key] is None or key_value_dict[key] == "": # To avoid null Values
					value = None
				else:
					value = int(key_value_dict[key])
				newElement.Day = value
			elif key == "ImdbId":
				newElement.ImdbId = key_value_dict[key]
			elif key == "TheTvDbId":
				newElement.TheTvDbId = key_value_dict[key]
			elif key == "TmDbId":
				newElement.TmDbId = key_value_dict[key]
			elif key == "Runtime":
				if key_value_dict[key] is None or key_value_dict[key] == "": # To avoid null Values
					value = None
				else:
					value = int(key_value_dict[key])
				newElement.Runtime = value
			#elif Resolution
			#elif Sound
			elif key == "Plot":
				newElement.Plot = key_value_dict[key]
			elif key == "Genres":
				newElement.Genres = key_value_dict[key]
			elif key == "Tag":
				newElement.Tag = key_value_dict[key]
			elif key == "Popularity":
				if key_value_dict[key] is None or key_value_dict[key] == "": # To avoid null Values
					value = None
				else:
					value = int(key_value_dict[key])
				newElement.Popularity = value
			elif key == "Season":
				newElement.Season = int(key_value_dict[key])
			elif key == "Episode":
				newElement.Episode = int(key_value_dict[key])
			
			elif key == "Path":
				newElement.Path = key_value_dict[key]
			elif key == "Filename":
				newElement.Filename = key_value_dict[key]
			elif key == "Extension":
				newElement.Extension = key_value_dict[key]
		return newElement

	def replaceByUsingPrimaryKey(self, type, primary_key, key_value_dict):
		printl("", self)
		element = self.getElementByUsingPrimaryKey(type, primary_key)
		if element is not None:
			newElement = element.copy()
			newElement = self.fillElement(newElement, key_value_dict)
			self.replace(element, (newElement, ))
			return newElement
		return None

	def addByUsingPrimaryKey(self, type, primary_key, key_value_dict):
		printl("", self)
		newElement = MediaInfo()
		if type == self.MOVIES and primary_key.has_key("imdbid"):
			newElement.ImdbId = primary_key["imdbid"]
			newElement.setMediaType(MediaInfo.MOVIE)
		
		elif type == self.TVSHOWS and primary_key.has_key("thetvdbid"):
			newElement.TheTvDbId = primary_key["thetvdbid"]
			newElement.setMediaType(MediaInfo.SERIE)
		
		elif type == self.TVSHOWSEPISODES and primary_key.has_key("thetvdbid") and primary_key.has_key("season") and primary_key.has_key("episode"):
			newElement.TheTvDbId = primary_key["thetvdbid"]
			newElement.Season = primary_key["season"]
			newElement.Episode = primary_key["episode"]
			newElement.setMediaType(MediaInfo.EPISODE)
		else:
			return None
		
		newElement = self.fillElement(newElement, key_value_dict)
		self.replace(None, (newElement, ))
		return newElement
	
	def getArtsByUsingPrimaryKey(self, type, primary_key, overwrite=False, backdrop=None, poster=None):
		printl("start changing arts", self)
		media = self.getElementByUsingPrimaryKey(type, primary_key)
		if media is not None:
			printl("element found ", self)
			if backdrop is not None:
				media.Backdrop = backdrop
				printl("setting backdrop source", self)
			if poster is not None:
				media.Poster = poster
				printl("setting poster source", self)
			
			if media.Backdrop is not None or media.Poster is not None:
				printl("downloading arts", self)
				Arts().download(media, overwrite)
				return True
			else:
				return False
		printl("no element found", self)
		return False

#
#################################   MOVIES   ################################# 
#
	# Pass throught functions
	def getMovies(self, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getMovies(order, firstRecord, numberOfRecords)

	def getMoviesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getMoviesValues(order, firstRecord, numberOfRecords)

	def getMoviesWithKey(self, movieKey):
		return self.db.getMoviesWithKey(movieKey)

	def getMoviesPkWithImdb(self, imdbId):
		return self.db.getMovieKeyWithImdb(imdbId)

	def getMoviesCount(self):
		return self.db.getMoviesCount()

#
#################################   SERIES   ################################# 
#
	# Pass throught functions	
	def getSeries(self, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getSeries(order, firstRecord, numberOfRecords)
		
	def getSeriesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getSeriesValues(order, firstRecord, numberOfRecords)
	
	def getSeriesWithKey(self, serieKey):
		return self.db.getSeriesWithKey(serieKey)
	
	def getSeriesWithTheTvDbId(self, theTvDbId):
		return self.db.getSeriesWithTheTvDbId(theTvDbId)
		
	def getSeriesEpisodes(self, serieKey=None, season=None):
		return self.db.getSeriesEpisodes(serieKey, season)
	
	def getSeriesEpisodesWithTheTvDbId(self, theTvDbId, season=None):
		return self.db.getSeriesEpisodesWithTheTvDbId(theTvDbId, season)
	
	def getSeriesEpisode(self, serieKey, season, episode):
		return self.db.getSeriesEpisode(serieKey, season, episode)
		
	def getSeriesSeasons(self, serieKey):			
		return self.db.getSeriesSeasons(serieKey)				

	def getSeriesCount(self):
		return self.db.getSeriesCount()

	def getSeriesCountSeasonsWithTheTvDbId(self, theTvDbId):
		return self.db.getSeriesCountSeasonsWithTheTvDbId(serieKey)

	def getSeriesCountSeasons(self, serieKey):
		return self.db.getSeriesCountSeasons(serieKey)
	
	def getSeriesCountEpisodesWithTheTvDbId(self, theTvDbId, season):
		return self.db.getSeriesCountEpisodesWithTheTvDbId(serieKey, season)
	
	def getSeriesCountEpisodes(self, serieKey=None, season=None):
		return self.db.getSeriesCountEpisodes(serieKey, season)


	def deleteSerieCascade(self, serieKey):
		return self.db.deleteSerieCascade(serieKey)
#	
#################################   FAILED   ################################# 
#
	# Pass throught functions	
	def getFailed(self):
		return self.db.getFailed()

	#def clearFailed(self):
	#	return self.db.deleteFailed()

	#def addFailed(self, entry):
	#	return self.db.insertFailed(entry)

	#def removeFailed(self, entry):
	#	return self.db.deleteFailed(entry)

#
###################################  UTILS  ###################################
#
	
	def convertNullValues(self, record):
		log("->", self, 10)
		if record.Year is None:
			record.Year = u""
		if record.Month is None:
			record.Month = u""
		return record


