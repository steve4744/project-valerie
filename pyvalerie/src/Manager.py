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
		elif type == self.FAILED:
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

	def remove(self, oldElement):
		printl("", self)
		if oldElement is not None:
			printl("oldElement=" + str(oldElement), self)
			if type(oldElement) is MediaInfo:
				b = self.db.remove(oldElement)
				printl("RM " + str(b), self)
				if b:
					Blacklist.add(oldElement.Filename + u"." + oldElement.Extension)
					Blacklist.save()
			else:
				self.db.removeFailed(oldElement)
				Blacklist.add(oldElement.Filename + u"." + oldElement.Extension)
				Blacklist.save()
