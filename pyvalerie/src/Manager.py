# -*- coding: utf-8 -*-

import Blacklist
import Config
from   Database import Database
from   MediaInfo import MediaInfo
from   MobileImdbComProvider import MobileImdbComProvider
import replace
from   sync import Sync

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class Manager(object):

	MOVIES = 0
	TVSHOWS = 1
	TVSHOWSEPISODES = 2
	FAILED = 3
	FAILED_ALL = 4
	
	def __init__(self):
		pass

	def start(self):
		printl("", self)
		Config.load()
		self.db = Database()
		self.db.reload()
		
		replace.load()

	def finish(self):
		printl("", self)
		self.db.save()

	def getAll(self, type, param=None):
		printl("type=" + str(type) + " param=" + str(param), self)
		if type == self.MOVIES:
			return self.db.dbMovies.values()
		elif type == self.TVSHOWS:
			return self.db.dbSeries.values()
		elif type == self.TVSHOWSEPISODES:
			list = []
			if param is not None:
				serie = param
				for season in self.db.dbEpisodes[serie]:
					list += self.db.dbEpisodes[serie][season].values()
			else:
				for serie in self.db.dbEpisodes:
					for season in self.db.dbEpisodes[serie]:
						list += self.db.dbEpisodes[serie][season].values()
						#for episode in self.db.dbEpisodes[serie][season]:
						#	if self.db.dbEpisodes[serie][season][episode].TheTvDbId == "79488":
						#		print self.db.dbEpisodes[serie][season][episode].Filename, serie, season, episode
			return list
		elif type == self.FAILED or type == self.FAILED_ALL:
			return self.db.dbFailed
		else:
			return None

	def searchAlternatives(self, oldElement):
		element = MediaInfo(oldElement.Path, oldElement.Filename, oldElement.Extension)
		if type(oldElement) is MediaInfo:	
			element.isMovie = oldElement.isMovie
			element.isSerie = oldElement.isSerie
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
			element.isSerie = True
			element.isMovie = False
		else:
			element.isSerie = False
			element.isMovie = True
		
		results = Sync().syncWithId(element)
		if results is not None:
			return results
		else:
			if istvshow is False:
				element.isSerie = True
				element.isMovie = False
			else:
				element.isSerie = False
				element.isMovie = True
			
			results = Sync().syncWithId(element)
			if results is not None:
				return results
		return None

	def replace(self, oldElement, newElement):
		printl("", self)
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
		element = None
		if type == self.MOVIES and primary_key.has_key("imdbid"):
			imdbid = primary_key["imdbid"]
			if self.db.dbMovies.has_key(imdbid):
				element = self.db.dbMovies[imdbid]
		elif type == self.TVSHOWS and primary_key.has_key("thetvdbid"):
			thetvdbid = primary_key["thetvdbid"]
			if self.db.dbSeries.has_key(thetvdbid):
				element = self.db.dbSeries[thetvdbid]
		elif type == self.TVSHOWSEPISODES and primary_key.has_key("thetvdbid") and primary_key.has_key("season") and primary_key.has_key("episode"):
			thetvdbid = primary_key["thetvdbid"]
			season = primary_key["season"]
			episode = primary_key["episode"]
			if self.db.dbEpisodes.has_key(thetvdbid) and self.db.dbEpisodes[thetvdbid].has_key(season) and self.db.dbEpisodes[thetvdbid][season].has_key(episode):
				element = self.db.dbEpisodes[thetvdbid][season][episode]
		
		return element

	def removeByUsingPrimaryKey(self, type, primary_key):
		element = self.getElementByUsingPrimaryKey(type, primary_key)
		if element is not None:
			self.remove(element, False)
			return True
		return False

	def fillElement(self, newElement, key_value_dict):
		for key in key_value_dict.keys():
			if key == "Title":
				newElement.Title = key_value_dict[key]
			elif key == "Year":
				newElement.Year = int(key_value_dict[key])
			elif key == "Month":
				newElement.Month = int(key_value_dict[key])
			elif key == "Day":
				newElement.Day = int(key_value_dict[key])
			elif key == "ImdbId":
				newElement.ImdbId = key_value_dict[key]
			elif key == "TheTvDbId":
				newElement.TheTvDbId = key_value_dict[key]
			elif key == "TmDbId":
				newElement.TmDbId = key_value_dict[key]
			elif key == "Runtime":
				newElement.Runtime = int(key_value_dict[key])
			#elif Resolution
			#elif Sound
			elif key == "Plot":
				newElement.Plot = key_value_dict[key]
			elif key == "Genres":
				newElement.Genres = key_value_dict[key]
			elif key == "Tag":
				newElement.Tag = key_value_dict[key]
			elif key == "Popularity":
				newElement.Popularity = int(key_value_dict[key])
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
		element = self.getElementByUsingPrimaryKey(type, primary_key)
		if element is not None:
			newElement = element
			newElement = self.fillElement(newElement, key_value_dict)
			self.replace(element, (newElement, ))
			return newElement
		return None

	def addByUsingPrimaryKey(self, type, primary_key, key_value_dict):
		newElement = MediaInfo()
		if type == self.MOVIES and primary_key.has_key("imdbid"):
			newElement.ImdbId = primary_key["imdbid"]
			newElement.isMovie = True
			newElement.isSerie = False
			newElement.isEpisode = False
		
		elif type == self.TVSHOWS and primary_key.has_key("thetvdbid"):
			newElement.TheTvDbId = primary_key["thetvdbid"]
			newElement.isMovie = False
			newElement.isSerie = True
			newElement.isEpisode = False
		
		elif type == self.TVSHOWSEPISODES and primary_key.has_key("thetvdbid") and primary_key.has_key("season") and primary_key.has_key("episode"):
			newElement.TheTvDbId = primary_key["thetvdbid"]
			newElement.Season = primary_key["season"]
			newElement.Episode = primary_key["episode"]
			newElement.isMovie = False
			newElement.isSerie = False
			newElement.isEpisode = True
		
		else:
			return None
		
		newElement = self.fillElement(newElement, key_value_dict)
		self.replace(None, (newElement, ))
		return newElement