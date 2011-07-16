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
#   r1 - 15/07/2011 - Zuki - Avoid null values on Dates, Popularity & Runtime
#
#   r
#
#   r
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

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

import os

class Manager():

	MOVIES = 0
	TVSHOWS = 1
	TVSHOWSSEASONS = 5
	TVSHOWSEPISODES = 2
	FAILED = 3
	FAILED_ALL = 4
	
	def __init__(self):
		printl("", self)
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
			return self.db.dbMovies.values()
		elif type == self.TVSHOWS:
			return self.db.dbSeries.values()
		elif type == self.TVSHOWSEPISODES:
			list = []
			if param is not None:
				serie = param
				if self.db.dbEpisodes.has_key(serie):
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
		
		elif type == self.TVSHOWSSEASONS: 
			#getAll(Manager.TVSHOWSSEASONS, (thetvdbid, )
			if param is not None and len(param) == 1:
				serie = param[0]
				if self.db.dbEpisodes.has_key(serie):
					return self.db.dbEpisodes[serie].keys()
			
			#getAll(Manager.TVSHOWSSEASONS, (thetvdbid, season, )
			elif param is not None and len(param) == 2:
				serie = param[0]
				season = param[1]
				if self.db.dbEpisodes.has_key(serie):
					if self.db.dbEpisodes[serie].has_key(season):
						return self.db.dbEpisodes[serie][season].values()
		
		elif type == self.FAILED or type == self.FAILED_ALL:
			return self.db.dbFailed
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
		printl("", self)
		printl("type=" + str(type), self)
		printl("primary_key=" + str(primary_key), self)
		element = None
		if type == self.MOVIES and primary_key.has_key("imdbid"):
			printl("isMovie found", self)
			imdbid = primary_key["imdbid"]
			#printl("type(imdbid)=" + str(type(imdbid)), self, "E")
			#for rec in self.db.dbMovies:	#printl("movie " + str(rec), self, "E")
			if self.db.dbMovies.has_key(imdbid):
				printl("has_key found", self)
				element = self.db.dbMovies[imdbid]
		elif type == self.TVSHOWS and primary_key.has_key("thetvdbid"):
			printl("isTvShow found", self)
			thetvdbid = primary_key["thetvdbid"]
			if self.db.dbSeries.has_key(thetvdbid):
				element = self.db.dbSeries[thetvdbid]
		elif type == self.TVSHOWSEPISODES and primary_key.has_key("thetvdbid") and primary_key.has_key("season") and primary_key.has_key("episode"):
			printl("isEpisode found", self)
			thetvdbid = primary_key["thetvdbid"]
			season = int(primary_key["season"])
			episode = int(primary_key["episode"])
			printl("Looking up episode", self, "D")
			print self.db.dbEpisodes.has_key(thetvdbid)
			print self.db.dbEpisodes[thetvdbid]
			print self.db.dbEpisodes[thetvdbid].has_key(season)
			print self.db.dbEpisodes[thetvdbid][season].has_key(episode)
			if self.db.dbEpisodes.has_key(thetvdbid) and self.db.dbEpisodes[thetvdbid].has_key(season) and self.db.dbEpisodes[thetvdbid][season].has_key(episode):
				element = self.db.dbEpisodes[thetvdbid][season][episode]
		
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
