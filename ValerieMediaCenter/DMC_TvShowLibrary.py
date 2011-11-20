# -*- coding: utf-8 -*-

import os

from DMC_Library import DMC_Library

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin
from Components.config import *
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

gAvailable = True

class DMC_TvShowLibrary(DMC_Library):

	def __init__(self, session):
		global Manager
		if Manager is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		
		self.manager = Manager("TVShows")
		DMC_Library.__init__(self, session, "tv shows")

	###
	# Return Value is expected to be:
	# (libraryArray, onEnterPrimaryKeys, onLeavePrimaryKeys, onLeaveSelectEntry
	def loadLibrary(self, primaryKeyValuePair, seenPng=None, unseenPng=None):
		global Manager
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
	
		printl("DEBUG 3", self)
	
		printl("", self)
		printl("primaryKeyValuePair=" + str(primaryKeyValuePair), self)
			
		# Diplay all TVShows
		if primaryKeyValuePair is None:
			printl("Series", self)
			parsedLibrary = []
			library = self.manager.getSeriesValues()
				
			tmpAbc = []
			tmpGenres = []
			for tvshow in library:
				d = {}
				
				d["ArtBackdropId"] = utf8ToLatin(tvshow.TheTvDbId)
				d["ArtPosterId"] = d["ArtBackdropId"]
				
				d["Id"]  = tvshow.Id
				d["ImdbId"]  = utf8ToLatin(tvshow.ImdbId)
				d["TheTvDbId"] = utf8ToLatin(tvshow.TheTvDbId)
				d["Title"]   = "  " + utf8ToLatin(tvshow.Title)
				if d["Title"][2].upper() not in tmpAbc:
					tmpAbc.append(d["Title"][2].upper())
				d["Tag"]     = utf8ToLatin(tvshow.Tag)
				d["Year"]    = tvshow.Year
				d["Month"]   = tvshow.Month
				d["Day"]     = tvshow.Day
				d["Plot"]    = utf8ToLatin(tvshow.Plot)
				d["Runtime"] = tvshow.Runtime
				d["Popularity"] = tvshow.Popularity
				d["Genres"]  = utf8ToLatin(tvshow.Genres).split("|")
				for genre in d["Genres"]:
					if genre not in tmpGenres:
						tmpGenres.append(genre)
				if config.plugins.pvmc.showseenforshow.value is True:
					if self.manager.isSeen({"TheTvDbId": d["TheTvDbId"]}):
						image = seenPng
					else:
						image = unseenPng
				else:
					image = None
					
				d["ScreenTitle"] = d["Title"]
				d["ScreenTitle"] = utf8ToLatin(d["ScreenTitle"])
				d["ViewMode"] = "ShowSeasons"
				parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50", image))
				
			sort = (("Title", None, False), ("Popularity", "Popularity", True), )
			
			filter = [("All", (None, False), ("", )), ]
			if len(tmpGenres) > 0:
				tmpGenres.sort()
				filter.append(("Genre", ("Genres", True), tmpGenres))
				
			if len(tmpAbc) > 0:
				tmpAbc.sort()
				filter.append(("Abc", ("Title", False, 1), tmpAbc))
				
			return (parsedLibrary, ("ViewMode", "Id", ), None, None, sort, filter)
		
		# Display the Seasons Menu
		#elif primaryKeyValuePair.has_key("ShowSeasons"):
		elif primaryKeyValuePair["ViewMode"]=="ShowSeasons":
			printl("Seasons", self)
			parsedLibrary = []
			
			tvshow = self.manager.getSerie(primaryKeyValuePair["Id"])
			d = {}
			
			d["ArtBackdropId"] = utf8ToLatin(tvshow.TheTvDbId)
			
			d["Id"]  = tvshow.Id
			d["ImdbId"]  = utf8ToLatin(tvshow.ImdbId)
			d["TheTvDbId"] = utf8ToLatin(tvshow.TheTvDbId)
			d["Tag"]     = utf8ToLatin(tvshow.Tag)
			d["Year"]    = tvshow.Year
			d["Month"]   = tvshow.Month
			d["Day"]     = tvshow.Day
			d["Plot"]    = utf8ToLatin(tvshow.Plot)
			d["Runtime"] = tvshow.Runtime
			d["Popularity"] = tvshow.Popularity
			d["Genres"]  = utf8ToLatin(tvshow.Genres).split("|")
			
			library = self.manager.getEpisodes(primaryKeyValuePair["Id"])
			
			seasons = []
			for entry in library:
				season = entry.Season
				if season not in seasons:
					seasons.append(season)
					s = d.copy()
					if entry.Season is None:
						s["Title"]  = "  Special"
						s["Season"] = "" # for retrive data only with season=None
					else:
						s["Title"]  = "  Season %2d" % (season, )
						s["Season"] = season
					
					s["ScreenTitle"] = tvshow.Title + " - " + s["Title"].strip()
					s["ScreenTitle"] = utf8ToLatin(s["ScreenTitle"])
					s["ArtPosterId"] = d["ArtBackdropId"] + "_s" + str(season)
					
					if config.plugins.pvmc.showseenforseason.value is True:
						if self.manager.isSeen({"TheTvDbId": d["TheTvDbId"], "Season": s["Season"]}):
							image = seenPng
						else:
							image = unseenPng
					else:
						image = None
					
					s["ViewMode"] = "ShowEpisodes"
					parsedLibrary.append((s["Title"], s, season, "50", image))
			sort = (("Title", None, False), )
			
			filter = [("All", (None, False), ("", )), ]
			
			return (parsedLibrary, ("ViewMode", "Id", "Season", ), None, primaryKeyValuePair, sort, filter)

		# Display the Episodes Menu
		#elif primaryKeyValuePair.has_key("TheTvDbId") and primaryKeyValuePair.has_key("Season"):
		elif primaryKeyValuePair["ViewMode"]=="ShowEpisodes":
			printl("EpisodesOfSeason", self)
			parsedLibrary = []
			
			#tvshow = self.manager.getElement...ByUsingPrimaryKey(Manager.TVSHOWS, \
			#	dict({'thetvdbid': primaryKeyValuePair["TheTvDbId"]}))
			
			#library = self.manager.getEpisodesWithTheTvDbId(primaryKeyValuePair["TheTvDbId"])
			tvshow  = self.manager.getSerie(primaryKeyValuePair["Id"])
			library = self.manager.getEpisodes(primaryKeyValuePair["Id"], primaryKeyValuePair["Season"])
			for episode in library:
				d = {}

				d["ArtBackdropId"] = utf8ToLatin(tvshow.TheTvDbId)
				d["ArtPosterId"] = d["ArtBackdropId"]
					
				d["Id"]  = episode.Id
				d["TVShowId"]  = tvshow.Id
				d["ImdbId"]  = utf8ToLatin(tvshow.ImdbId)
				d["TheTvDbId"] = utf8ToLatin(episode.TheTvDbId)
				d["Tag"]     = utf8ToLatin(tvshow.Tag)
				#d["Title"]   = "  %dx%02d: %s" % (episode.Season, episode.Episode, utf8ToLatin(episode.Title), )
				if episode.Season is None and episode.Disc is None and episode.Episode is not None: # 
					# Only Episode
					d["Title"]   = "  %s: %s" % (episode.Episode, utf8ToLatin(episode.Title), )
				elif episode.Season is None and episode.Disc is not None and episode.Episode is None: 
					# Only Disc
					d["Title"]   = "  Disc %s: %s" % (episode.Disc, utf8ToLatin(episode.Title), )
				elif episode.Season is not None and episode.Disc is None and episode.Episode is not None: # 
					# Without Disc
					d["Title"]   = "  %02d: %s" % (episode.Episode, utf8ToLatin(episode.Title), )
				elif episode.Season is not None and episode.Disc is not None and episode.Episode is None: # 
					# Without Episode
					d["Title"]   = "  Disc %s: %s" % (episode.Disc, utf8ToLatin(episode.Title), )
				else:
					d["Title"]   = "  %s" % (utf8ToLatin(episode.Title), )
					
				if episode.Season is None:
					d["ScreenTitle"] = tvshow.Title + " - " + "Special"
				else:
					d["ScreenTitle"] = tvshow.Title + " - " + "Season %2d" % (episode.Season, )
				d["ScreenTitle"] = utf8ToLatin(d["ScreenTitle"])
				d["Year"]    = episode.Year
				d["Month"]   = episode.Month
				d["Day"]     = episode.Day
				d["Path"]    = utf8ToLatin(episode.Path + "/" + episode.Filename + "." + episode.Extension)
				if self.checkFileCreationDate:
					try:
						d["Creation"] = os.stat(d["Path"]).st_mtime
					except Exception, ex:
						printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
						d["Creation"] = 0
				d["Season"]  = episode.Season
				d["Episode"] = episode.Episode
				d["Plot"]    = utf8ToLatin(episode.Plot)
				d["Runtime"] = episode.Runtime
				d["Popularity"] = episode.Popularity
				d["Genres"]  = utf8ToLatin(episode.Genres).split("|")
				d["Resolution"]  = utf8ToLatin(episode.Resolution)
				d["Sound"]  = utf8ToLatin(episode.Sound)
				
				if self.manager.isSeen({"TheTvDbId": d["TheTvDbId"], "Episode":episode.Episode, "Season": episode.Season}):
					image = seenPng
					d["Seen"] = "Seen"
				else:
					image = unseenPng
					d["Seen"] = "Unseen"
				
				d["ViewMode"] = "play"
				_season = episode.Season
				if _season is None:
					_season=0
				_disc = episode.Disc
				if _disc is None:
					_disc=0
				_episode = episode.Episode
				if _episode is None:
					_episode=0
				printl("DISC: " + repr(_disc), self)
				_season  = int(_season)
				_disc    = int(_disc)
				_episode = int(_episode)
					
				parsedLibrary.append((d["Title"], d, _season * 100000 + _disc * 1000 + _episode, "50", image))
			sort = [("Title", None, False), ("Popularity", "Popularity", True), ]
			if self.checkFileCreationDate:
				sort.append(("File Creation", "Creation", True))
			
			filter = [("All", (None, False), ("", )), ]
			filter.append(("Seen", ("Seen", False, 1), ("Seen", "Unseen", )))
			
			return (parsedLibrary, ("ViewMode", "Id", "TVShowId", "Season", "Episode", ), dict({ \
				'ViewMode': "ShowSeasons", \
				'Id': primaryKeyValuePair["Id"], \
				}), primaryKeyValuePair, sort, filter)
			
		return None

	def getPlaybackList(self, entry):
		playbackList = []
		
		primaryKeyValuePair = {}
		primaryKeyValuePair["Id"] = entry["TVShowId"]
		primaryKeyValuePair["Season"] = entry["Season"]
		primaryKeyValuePair["ViewMode"] = "ShowEpisodes"
		library = self.loadLibrary(primaryKeyValuePair)[0]
		
		playbackList.append( (entry["Path"], entry["Title"], entry, ))
		nextEpisode = entry["Episode"] + 1
		
		found = True
		while found is True:
			found = False
			for episode in library:
				episodeDict = episode[1]
				if episodeDict["Episode"] == nextEpisode:
					playbackList.append( (episodeDict["Path"], episodeDict["Title"], episodeDict, ))
					nextEpisode += 1
					found = True
					break
		
		return playbackList

	def buildInfoPlaybackArgs(self, entry):
		args = {}
		args["id"] 	= entry["Id"]
		args["title"]   = entry["Title"]
		args["year"]    = entry["Year"]
		args["thetvdb"] = entry["TheTvDbId"]
		args["season"]  = entry["Season"]
		args["episode"] = entry["Episode"]
		args["type"]    = "tvshow"
		return args

if gAvailable is True:
	registerPlugin(Plugin(name=_("TV Shows"), start=DMC_TvShowLibrary, where=Plugin.MENU_VIDEOS, weight=4))
