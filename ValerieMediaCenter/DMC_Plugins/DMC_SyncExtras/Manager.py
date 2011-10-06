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
#   v  - 15/09/2011 - Zuki - Convert Db's to one file - mediafiles.db
#			     Changes to webif/sync by Don 	
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import os
import Blacklist
import replace

from   PVS_DatabaseHandler import Database
from   MediaInfo import MediaInfo
from   MobileImdbComProvider import MobileImdbComProvider

from sync import Sync
from Arts import Arts

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin

class Manager():

	# make ID's equal in MediaInfo & Manager, hope there is nothing hardcoded...
	MOVIES 	= 1 #0
	TVSHOWS = 2 #1
	TVSHOWSEPISODES = 3 #2
	MUSIC = 4

	TVSHOWSSEASONS = 5
	FAILED = 6
	FAILED_ALL = 7
	
	ORDER_TITLE = 1
	ORDER_YEAR  = 2

	def __init__(self):
		printl("->", self)
		try:
			self.db = Database().getInstance()
			replace.load()
		except Exception, ex:
			printl ("Exception on Init Ex:"+str(ex), self)
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.sync import checkDefaults
			checkDefaults()
			
			self.db = Database().getInstance()
			replace.load()

	def finish(self):
		printl("", self)
		self.db.save()

	def getAll(self, type, param=None):
		printl("type=" + str(type) + " param=" + str(param), self)
					
		if type == self.MOVIES:
			return self.getMoviesValues()
					
		elif type == self.TVSHOWS:
			return self.getSeriesValues()
			
		elif type == self.TVSHOWSEPISODES:
			list = []
			if param is not None:
				### todo: CONVERT TO ID, don't use tvdbid
				list = self.db.getEpisodesWithTheTvDbId(param)
			else:
				list = self.db.getEpisodes()
			return list
		
		#not used
		elif type == self.TVSHOWSSEASONS: 
			#get-ll(Manager.TVSHOWSSEASONS, (thetvdbid, )
			if param is not None and len(param) == 1:
				list = self.db.getSeriesSeasons(param[0])

			#get-All(Manager.TVSHOWSSEASONS, (thetvdbid, season, )
			elif param is not None and len(param) == 2:
				serie  = param[0]
				season = param[1]
				list = self.db.getEpisodesWithKey(serie, season)
			
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

	#not used anymore - replacement: update/insert media
	def replace(self, oldElement, newElement):
		printl("", self)
		# not consistent ...todo: update serie
		if oldElement is not None:
			printl("oldElement=" + str(oldElement), self)
			if type(oldElement) is MediaInfo:
				printl("RM " + str(self.db.remove(oldElement)), self)
			#else:
			#	self.db.removeFailed(oldElement)
		
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
			#else:
			#	self.db.removeFailed(oldElement)
			#	Blacklist.add(oldElement.Filename + u"." + oldElement.Extension)
			#	Blacklist.save()

	def getElementByUsingPrimaryKey(self, type, primary_key):
		printl("", self)
		printl("type=" + str(type), self)
		printl("primary_key=" + str(primary_key), self)
		element = None
		if type == self.MOVIES and primary_key.has_key("imdbid"):
			printl("is_Movie found", self)
			imdbid = primary_key["imdbid"]
			element = self.db.getMediaWithImdbId(imdbid)
		
		elif type == self.TVSHOWS and primary_key.has_key("thetvdbid"):
			printl("is_TvShow found", self)
			thetvdbid = primary_key["thetvdbid"]
			element = self.db.getMediaWithTheTvDbId(thetvdbid)
		
		elif type == self.TVSHOWSEPISODES and primary_key.has_key("thetvdbid") and primary_key.has_key("season") and primary_key.has_key("episode"):
			printl("is_Episode found", self)
			thetvdbid = primary_key["thetvdbid"]
			season = int(primary_key["season"])
			episode = int(primary_key["episode"])
			printl("Looking up episode", self, "D")
			element = self.db.getSeriesEpisode(thetvdbid, season, episode)
		
		return element
	
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
	
	def isSeen(self, primary_key):
		if primary_key.has_key("TheTvDbId"):
			if primary_key.has_key("Season"):
				if primary_key.has_key("Episode"):
					return self.isEntrySeen(primary_key)
				else:
				    return self.isSeasonSeen(primary_key)
			else:
				return self.isShowSeen(primary_key)
		elif primary_key.has_key("ImdbId"):
			return self.isEntrySeen(primary_key)
		
		return False
	
#
##########################  SEEN - not in dbHandler  ########################## 
#

	def isShowSeen(self, primary_key):
		library = self.getAll(Manager.TVSHOWSEPISODES, primary_key["TheTvDbId"])
		
		for episode in library:
			if not self.isEntrySeen({"TheTvDbId": primary_key["TheTvDbId"], "Episode":episode.Episode, "Season": episode.Season}):
				return False
		return True
	
	def isSeasonSeen(self, primary_key):
		library = self.getAll(Manager.TVSHOWSEPISODES, primary_key["TheTvDbId"])
		
		for episode in library:
			if episode.Season == primary_key["Season"]:
				if not self.isEntrySeen({"TheTvDbId": primary_key["TheTvDbId"], "Episode":episode.Episode, "Season": episode.Season}):
					return False
		return True
	
	def isEntrySeen(self, primary_key):
		plugins = getPlugins(where=Plugin.INFO_SEEN)
		for plugin in plugins:
			if plugin.fnc(primary_key):
				return True
			
		return False
#
###############################   MEDIA FILES   ############################### 
#
	def insertMedia(self, type, key_value_dict):
		key_value_dict["MediaType"] = type	
		if not self.db.insertMediaWithDict(key_value_dict):
			printl("Insert Media - Failed", self)	
			return False
		return True
			
	def updateMedia(self, type, key_value_dict):
		key_value_dict["MediaType"] = type
		if not self.db.updateMediaWithDict(key_value_dict):
			printl("Update Media - Failed", self)	
			return False
		return True
	
	def deleteMedia(self, type, id):
		if not self.db.deleteMedia(id):
			printl("Delete Media - Failed", self)	
			return False
		return True
	
	def getMediaPaths(self):
		return self.db.getMediaPaths()
	
	def getMediaValuesForFolder(self, type, path, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getMediaValuesForFolder(type, path, order=None, firstRecord=0, numberOfRecords=9999999)
	
#
#################################   MOVIES   ################################# 
#
	# Pass throught functions

	# for test 
	def getDbDump(self):
		return self.db.getDbDump()
		
	def dbIsCommited(self):
		return self.db.dbIsCommited()
		
	def getMoviesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getMediaValues(MediaInfo.MOVIE, order, firstRecord, numberOfRecords)

	def getMovie(self, id):
		return self.db.getMediaWithId(id)

	def getMoviesCount(self):
		return self.db.getMediaCount(MediaInfo.MOVIE)

	def changeMediaArts(self, type, id, overwrite=False, backdrop=None, poster=None):
		printl("start changing arts 2", self)
		m = None
		if type == self.MOVIES:
			m = self.db.getMediaWithId(id)
		elif type == self.TVSHOWS:
			m = self.db.getMediaWithId(id)		
		elif type == self.TVSHOWSEPISODES:
			m = self.db.getMediaWithId(id)
		elif type == self.MUSIC:
			pass
			#m = self.db.getMediaWithId(id)
			return False
		else:
			return None				

		if m is None:
			printl("Change Media Art - DB Error - Not found", self)	
			return False
		
		if backdrop is not None:
			m.Backdrop = backdrop
		if poster is not None:
			m.Poster = poster
		
		if m.Backdrop is not None or m.Poster is not None:
			printl("downloading arts", self)
			Arts().download(m, overwrite)
			return True
		else:
			return False
	
		return False
#
#################################   SERIES   ################################# 
#
	# Pass throught functions
		
	def getSeriesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getMediaValues(MediaInfo.SERIE, order, firstRecord, numberOfRecords)
	
	def getSerie(self, id):
		return self.db.getMediaWithId(id)

	def getSeriesWithTheTvDbId(self, theTvDbId):
		return self.db.getMediaWithTheTvDbId(theTvDbId)
		
	def getSeriesCount(self):
		return self.db.getMediaCount(MediaInfo.SERIE)
		
	def getEpisodes(self, id):
		return self.db.getEpisodes(id)
	
	def getEpisodesCount(self, mediaId=None, season=None):
		return self.db.getEpisodesCount(mediaId, season)

	def getEpisode(self, id):
		return self.db.getEpisode(id)

#	
#################################   FAILED   ################################# 
#
	def getFailed(self):
		return self.db.getFailed()
		
	def getFailedItem(self, id):
		return self.db.getMediaWithId(id)
		
	def getFailedCount(self):
		return self.db.getFailedCount()
		
#
###################################  UTILS  ###################################
#
	