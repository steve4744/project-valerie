from enigma import eTimer, eWidget, eRect, eServiceReference, iServiceInformation, iPlayableService, ePicLoad
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Components.Button import Button

from Components.Sources.List import List
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen

from Components.ServicePosition import ServicePositionGauge
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *

from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
#from Screens.DMC_MoviePlayer import PVMC_MoviePlayer
from Screens.InfoBar import MoviePlayer

from Plugins.Plugin import PluginDescriptor


from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap

import os
from os import path as os_path

from DMC_Global import Showiframe
from DMC_Player import PVMC_Player 
from DataElement import DataElement
import math

from TraktAPI import TraktAPI 

#------------------------------------------------------------------------------------------

class PVMC_Series(Screen, HelpableScreen, InfoBarBase):

	def __init__(self, session):
		Screen.__init__(self, session)
		InfoBarBase.__init__(self)
		HelpableScreen.__init__(self)
		self.showiframe = Showiframe()
		
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()	

		self.isVisible = True
		self.inSeries = True
		self.inSeasons = False
		self.inEpisode = False
		self.rememeberSeriesIndex = 0
		self.selectedSeries = 0
		self.serieslist = []
		self.moviedb = {}
		self.episodesdb = {}
		
		list = []
		self["listview"] = List(list, True)
		self["poster"] 				= Pixmap()
		self["title"] 				= Label()
		self["otitle"] 				= Label()
		self["tag"] 				= Label()
		self["shortDescription"] 	= Label()
		self["director"] 			= Label()
		self["writer"] 				= Label()
		self["genre"] 				= Label()
		self["year"] 				= Label()
		self["runtime"] 			= Label()
		
		self["total"] = Label()
		self["current"] = Label()
		
		self.ShowStillPicture = False
		
		try:
			from StillPicture import StillPicture
			self["backdrop"] = StillPicture()
			self.ShowStillPicture = True
		except Exception, ex:
			print ex
		
		self["listview_itemsperpage"] = DataElement()
		
		for i in range(10):
			stars = "star" + str(i)
			print stars
			self[stars] = Pixmap()
			if self[stars].instance is not None:
				self[stars].instance.hide()

		for i in range(10):
			stars = "nostar" + str(i)
			print stars
			self[stars] = Pixmap()
		
		self.backdropquality = ""
		if config.plugins.pvmc.backdropquality.value == "Low":
			self.backdropquality = "_low"
		
		if os.path.exists(u"/hdd/valerie/tvshows.txd"):
				self.USE_DB_VERSION = self.DB_TXD
		
		self["actions"] = HelpableActionMap(self, "PVMC_AudioPlayerActions", 
			{
				"ok": (self.KeyOk, "Play selected file"),
				"cancel": (self.KeyExit, "Exit Audio Player"),
				"left": (self.leftUp, "List Top"),
				"right": (self.rightDown, "List Bottom"),
				"up": (self.up, "List up"),
				"down": (self.down, "List down"),
				"up_quick": (self.up_quick, "List up"),
				"down_quick": (self.down_quick, "List down"),
				"up_first": (self.up_quick, "List up"),
				"down_first": (self.down_quick, "List down"),
				"info": (self.KeyInfo, "show Plot"),

			}, -2)
		
		if self.USE_DB_VERSION == self.DB_TXT:
			self.loadSeriesDB()
		elif self.USE_DB_VERSION == self.DB_TXD:
			self.loadSeriesTxd()
		
		print "TRAKT.TV: ", config.plugins.pvmc.trakt.value
		if config.plugins.pvmc.trakt.value is True:
			self.trakt = TraktAPI("pvmc")
			self.trakt.setUsernameAndPassword(config.plugins.pvmc.traktuser.value, config.plugins.pvmc.traktpass.value)
			self.trakt.setType(TraktAPI.TYPE_TVSHOW)

		self.onFirstExecBegin.append(self.refresh)

	DB_TXT = 1
	DB_TXD = 2
	DB_PICKLE = 3
	DB_SQLITE= 4
	USE_DB_VERSION = DB_TXT

	FAST_STILLPIC = False

	def loadSeriesTxd(self):
		list =[]
		entrys =[]
		try:
			if self.inSeries:
				self.serieslist=[]
				db = open("/hdd/valerie/tvshows.txd").read()[:-1]
			elif self.inSeasons:
				db = open("/hdd/valerie/episodes/" + self.selectedSeries + ".txd").read()[:-1]
			
			if not self.inEpisode:
				lines = db.split("\n")
				version = lines[0]
				linesLen = len(lines)
			
			if self.inSeries:
				#self.moviedb.clear()
				for i in range(1, linesLen, 9):
					print lines[i+0]
					if lines[i+0] == "EOF":
						break
					d = {} 
					d["ImdbId"]    = lines[i+0]
					d["TheTvDb"]   = lines[i+1]
					d["Title"]     = lines[i+2]
					d["Tag"]       = lines[i+3]
					d["Year"]      = lines[i+4]
					
					d["Plot"]       = lines[i+5]
					d["Runtime"]    = lines[i+6]
					d["Popularity"] = lines[i+7]
					
					d["Genres"] = lines[i+8]
					
					# deprecated
					d["Directors"] = ""
					d["Writers"]   = ""
					d["OTitle"]    = ""
					
					self.moviedb[d["TheTvDb"]] = d
					if not d["Title"] in entrys:
						entrys.append(d["Title"])
						self.serieslist.append(("  " + d["Title"], d["TheTvDb"], "menu_globalsettings", "50"))
					
			elif self.inSeasons:
				self.episodesdb.clear()
				for i in range(1, linesLen, 12):
					if lines[i+0] == "EOF":
						break
					d = {} 
					d["TheTvDb"]    = lines[i+0]
					d["Title"]     = lines[i+1]
					d["Tag"]       = ""
					d["Year"]      = lines[i+2]
					
					d["Path"] = lines[i+3] + "/" + lines[i+4] + "." + lines[i+5]
					
					d["Season"]       = int(lines[i+6])
					d["Episode"]      = int(lines[i+7])
					
					d["Plot"]       = lines[i+8]
					d["Runtime"]    = lines[i+9]
					d["Popularity"] = lines[i+10]
					
					d["Genres"] = lines[i+11]
					
					# deprecated
					d["Directors"] = ""
					d["Writers"]   = ""
					d["OTitle"]    = ""
					
					if d["Season"] == -1:
						continue
					
					#self.moviedb[d["Season"] * 100 + d["Episode"]] = d
					self.episodesdb[d["Season"] * 100 + d["Episode"]] = d
					if not d["Season"] in entrys:
						entrys.append(d["Season"])
						list.append(("  " + "Season " + str(d["Season"]), str(d["Season"]), "menu_globalsettings", "50"))
			else:
				for episode in self.episodesdb:
					d = self.episodesdb[episode]
					if d["Season"] == self.selectedSeason:
						if not d["Episode"] in entrys:
							entrys.append(d["Episode"])
							list.append(("  " + str(d["Season"])+"x"+("%02d" % d["Episode"]) + ": " + d["Title"], d["Season"] * 100 + d["Episode"], "menu_globalsettings", "50"))
							
		except OSError, e: 
			print "OSError: ", e
		except IOError, e: 
			print "OSError: ", e
		
		if self.inSeries:
			self.serieslist.sort()
			
			self["listview"].setList(self.serieslist)	
		elif self.inSeasons:
			list.sort()
			self["listview"].setList(list)
		elif self.inEpisode:
			list.sort()
			self["listview"].setList(list)
			
		self["listview"].setIndex(0)
		self.refresh()

	def loadSeriesDB(self):
		list =[]
		filter = []
		entrys =[]
		if self.inSeries or self.inEpisode:
			filter.append("Tag")
			filter.append("Plot")
			filter.append("Directors")
			filter.append("Writers")
			filter.append("Genres")
			filter.append("Year")
			filter.append("Runtime")
			filter.append("Popularity")
			filter.append("ImdbId")
			filter.append("Title")
			filter.append("OTitle")
			filter.append("TheTvDb")
			filter.append("Path")
		if self.inSeasons or self.inEpisode:
			filter.append("Season")
			filter.append("Episode")
				
		try:
			if self.inSeries:
				self.serieslist=[]
				db = open("/hdd/valerie/seriesdb.txt").read()[:-1]
			else:
				db = open("/hdd/valerie/episodes/" + self.selectedSeries + ".txt").read()[:-1]
					
			movies = db.split("\n----END----\n")
			
			for movie in movies:
				movie = movie.split("---BEGIN---\n")
				if len(movie) == 2: 
					d = {} 
					lines = movie[1].split('\n')
					for line in lines: 
						#print "Line: ", line
						if ":" in line: 
							key, text = (s.strip() for s in line.split(":", 1)) 
						if key in filter: 
							d[key] = text
					
					if "Season" in d:
						d["Season"] = int(d["Season"])
					
					if "Episode" in d:
						d["Episode"] = int(d["Episode"])
					
					#print d
					if self.inSeries:
						self.moviedb[d["TheTvDb"]] = d
						if not d["Title"] in entrys:
							entrys.append(d["Title"])
							self.serieslist.append(("  " + d["Title"], d["TheTvDb"], "menu_globalsettings", "50"))
					elif self.inSeasons:
						self.episodesdb[d["Season"] * 100 + d["Episode"]] = d
						if not d["Season"] in entrys:
							entrys.append(d["Season"])
							list.append(("  " + "Season " + str(d["Season"]), str(d["Season"]), "menu_globalsettings", "50"))
					else:
						for episode in self.episodesdb:
							d = self.episodesdb[episode]
							if d["Season"] == self.selectedSeason:
								if not d["Episode"] in entrys:
									entrys.append(d["Episode"])
									list.append(("  " + str(d["Season"])+"x"+("%02d" % d["Episode"]) + ": " + d["Title"], d["Season"] * 100 + d["Episode"], "menu_globalsettings", "50"))
		
		except OSError, e: 
			print "OSError: ", e
		except IOError, e: 
			print "OSError: ", e
		
		if self.inSeries:
			self.serieslist.sort()
			self["listview"].setList(self.serieslist)	
		elif self.inSeasons:
			list.sort()
			self["listview"].setList(list)
		elif self.inEpisode:
			list.sort()
			self["listview"].setList(list)
			
		self["listview"].setIndex(0)
		self.refresh()
			

	def setText(self, name, value, ignore=False, what=None):
		try:
			if self[name]:
				if len(value) > 0:
					self[name].setText(value)
				elif ignore is False:
					if what is None:
						self[name].setText("Not available")
					else:
						self[name].setText(what + " not available")
				else:
					self[name].setText(" ")
		except Exception, ex:
			print "setText::", ex

	def refresh(self, changeBackdrop=True):
		selection = self["listview"].getCurrent()
		if selection is not None and type(selection) != bool:
			if self.inSeries is True:
				if self.ShowStillPicture is True:
					if changeBackdrop is True:
						if os.access("/hdd/valerie/media/" + selection[1] + "_backdrop" + self.backdropquality + ".m1v", os.F_OK):
							self["backdrop"].setStillPicture("/hdd/valerie/media/" + selection[1] + "_backdrop" + self.backdropquality + ".m1v")
						elif os.access("/hdd/valerie/media/" + selection[1] + "_backdrop" + self.backdropquality + ".mvi", os.F_OK):
							self["backdrop"].setStillPicture("/hdd/valerie/media/" + selection[1] + "_backdrop" + self.backdropquality + ".mvi")
						else:
							self["backdrop"].setStillPictureToDefault()
						
				if self["poster"].instance is not None:
					if os.access("/hdd/valerie/media/" + selection[1] + "_poster.png", os.F_OK):
						self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + selection[1] + "_poster.png")
					else:
						self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/defaultposter.png")
						
				self.setText("title", selection[0])
				self.setText("otitle", "---") #self.moviedb[selection[1]]["OTitle"])
				self.setText("tag", self.moviedb[selection[1]]["Tag"], True)
				
				self.setText("shortDescription", self.moviedb[selection[1]]["Plot"], what="Overview")
				
				if self.moviedb[selection[1]].has_key("Directors"):
					self.setText("director", self.moviedb[selection[1]]["Directors"])
				if self.moviedb[selection[1]].has_key("Writers"):
					self.setText("writer", self.moviedb[selection[1]]["Writers"])
					
				self.setText("genre", self.moviedb[selection[1]]["Genres"].replace('|', ", "), what="Genre")
				self.setText("year", str(self.moviedb[selection[1]]["Year"]))
				self.setText("runtime", self.moviedb[selection[1]]["Runtime"] + " min")
				
				#itemsPerPage = int(self["listview_itemsperpage"].getData())
				#itemsTotal = self["listview"].count()
				#print "itemsPerPage", itemsPerPage
				#pageTotal = int(math.ceil((itemsTotal / itemsPerPage) + 0.5))
				#pageCurrent = int(math.ceil((self["listview"].getIndex() / itemsPerPage) + 0.5))
				#self.setText("total", "Total movies: " + str(itemsTotal))
				#self.setText("current", str(pageCurrent) + "/" + str(pageTotal))
				
				for i in range(int(self.moviedb[selection[1]]["Popularity"])):
					if self["star" + str(i)].instance is not None:
						self["star" + str(i)].instance.show()

				for i in range(10 - int(self.moviedb[selection[1]]["Popularity"])):
					if self["star" + str(9 - i)].instance is not None:
						self["star" + str(9 - i)].instance.hide()

			elif self.inEpisode is True:
				self.setText("title", selection[0])
				self.setText("shortDescription", self.episodesdb[selection[1]]["Plot"], what="Overview")
			
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			#print "itemsPerPage", itemsPerPage
			pageTotal = int(math.ceil((itemsTotal / itemsPerPage) + 0.5))
			pageCurrent = int(math.ceil((self["listview"].getIndex() / itemsPerPage) + 0.5))
			if self.inSeries:
				self.setText("total", "Total tv shows: " + str(itemsTotal))
			elif self.inSeasons:
				self.setText("total", "Total seasons: " + str(itemsTotal))
			elif self.inEpisode:
				self.setText("total", "Total episodes: " + str(itemsTotal))
			self.setText("current", str(pageCurrent) + "/" + str(pageTotal))

	def up(self):
		print "PVMC_Series::up"
		#self["listview"].up()
		if self.FAST_STILLPIC is False:
			self.refresh()

	def up_first(self):
		print "PVMC_Series::up_first"
		#self["listview"].up()
		if self.FAST_STILLPIC is False:
			self.refresh()

	def up_quick(self):
		print "PVMC_Series::up_quick"
		self["listview"].selectPrevious()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def down(self):
		print "PVMC_Series::down"
		#self["listview"].down()
		if self.FAST_STILLPIC is False:
			self.refresh()

	def down_first(self):
		print "PVMC_Series::down_first"
		#self["listview"].down()
		if self.FAST_STILLPIC is False:
			self.refresh()

	def down_quick(self):
		print "PVMC_Series::down_quick"
		self["listview"].selectNext()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def leftUp(self):
		itemsPerPage = int(self["listview_itemsperpage"].getData())
		itemsTotal = self["listview"].count()
		index = self["listview"].getIndex() - itemsPerPage
		if index < 0:
			index = 0
		self["listview"].setIndex(index)
		#self["listview"].pageUp()
		self.refresh()
		
	def rightDown(self):
		itemsPerPage = int(self["listview_itemsperpage"].getData())
		itemsTotal = self["listview"].count()
		index = self["listview"].getIndex() + itemsPerPage
		if index >= itemsTotal:
			index = itemsTotal - 1
		self["listview"].setIndex(index)
		#self["listview"].pageDown()
		self.refresh()

	#def visibility(self, show):
	#	if self.isVisible is True and show is False:
	#		self.isVisible = False
	#		self.hide()
	#	elif self.isVisible is False and show is True:
	#		self.isVisible = True
	#		self.show()

	def KeyOk(self):

		selection = self["listview"].getCurrent()
		if selection is not None:
			if self.inSeries is True:
				self.inSeries = False
				self.inSeasons = True
				self.inEpisode = False
				
				self.selectedSeries = selection[1]
				self.rememeberSeriesIndex = self["listview"].getIndex()
				
				seasonslist = []
				self.seasonsdb = {}
				
				
				if self.USE_DB_VERSION == self.DB_TXT:
					self.loadSeriesDB()
				elif self.USE_DB_VERSION == self.DB_TXD:
					self.loadSeriesTxd()
		
				self.refresh()
				
			elif self.inSeasons is True:
				self.inSeries = False
				self.inSeasons = False
				self.inEpisode = True

				self.selectedSeason = int(selection[1])
				self.rememeberSeasonsIndex = self["listview"].getIndex()

				if self.USE_DB_VERSION == self.DB_TXT:
					self.loadSeriesDB()
				elif self.USE_DB_VERSION == self.DB_TXD:
					self.loadSeriesTxd()
		
				self.refresh()

			elif self.inEpisode is True:
				if self.isVisible == False:
					self.visibility()
					return
		
				selection = self["listview"].getCurrent()
				if selection is not None:
					playbackPath = self.episodesdb[selection[1]]["Path"]
					if os.path.isfile(playbackPath):
						self.showiframe.finishStillPicture()

						playbackList = []
						self.currentSeasonNumber = self.episodesdb[selection[1]]["Season"]
						self.currentEpisodeNumber = self.episodesdb[selection[1]]["Episode"]
						i = 0
						while True:
							key = self.currentSeasonNumber *100 + self.currentEpisodeNumber + i
							if key in self.episodesdb:
								d = self.episodesdb[key]
								playbackList.append( (self.episodesdb[key]["Path"], str(d["Season"])+"x"+("%02d" % d["Episode"]) + ": " + self.episodesdb[key]["Title"]), )
								i = i + 1
							else:
								break
							
						print "PLAYBACK: ", playbackList
						if config.plugins.pvmc.trakt.value is True:
							self.trakt.setName(self.moviedb[self.episodesdb[selection[1]]["TheTvDb"]]["Title"])
							self.trakt.setYear(self.moviedb[self.episodesdb[selection[1]]["TheTvDb"]]["Year"])
							self.trakt.setSeasonAndEpisode(self.currentSeasonNumber, self.currentEpisodeNumber)
							self.trakt.setStatus(TraktAPI.STATUS_WATCHING)
							self.trakt.setTheTvDbId(self.episodesdb[selection[1]]["TheTvDb"])
							self.trakt.send()
						self.session.openWithCallback(self.leaveMoviePlayer, PVMC_Player, playbackList, self.notifyNextEntry)
						#self.visibility(False)
					else:
						self.session.open(MessageBox, "Not found!\n" + self.episodesdb[selection[1]]["Path"] + "\n\nPlease make sure that your drive is connected/mounted.", type = MessageBox.TYPE_ERROR)

	def KeyInfo(self):
		selection = self["listview"].getCurrent()
		if self.inEpisode is True:
			self.session.open(MessageBox, "Title:\n" + self.episodesdb[selection[1]]["Title"] + "\n\nPlot:\n" + self.episodesdb[selection[1]]["Plot"], type = MessageBox.TYPE_INFO)
		elif self.inSeries is True:
			if selection is not None:
				self.session.open(MessageBox, "Title:\n" + self.moviedb[selection[1]]["Title"] + "\n\nPlot:\n" + self.moviedb[selection[1]]["Plot"], type = MessageBox.TYPE_INFO)
		

	def notifyNextEntry(self):
		print "PVMC_Series::notifyNextEntry"
		if config.plugins.pvmc.trakt.value is True:
			self.trakt.setStatus(TraktAPI.STATUS_WATCHED)
			self.trakt.send()
		
		self.currentEpisodeNumber = str(int(self.currentEpisodeNumber) + 1)
		
		if config.plugins.pvmc.trakt.value is True:
			self.trakt.setSeasonAndEpisode(self.currentSeasonNumber, self.currentEpisodeNumber)
			self.trakt.setStatus(TraktAPI.STATUS_WATCHING)
			self.trakt.send()


	def leaveMoviePlayer(self): 
		if config.plugins.pvmc.trakt.value is True:
			self.trakt.setStatus(TraktAPI.STATUS_WATCHED)
			self.trakt.send()
		self.session.nav.playService(None) 
		#self.visibility(True)
		if os.access("/hdd/valerie/media/" + self.selectedSeries + "_backdrop" + self.backdropquality + ".m1v", os.F_OK):
			self.showiframe.showStillpicture("/hdd/valerie/media/" + self.selectedSeries + "_backdrop" + self.backdropquality + ".m1v")
		else:
			self.showiframe.showStillpicture("/hdd/valerie/media/defaultbackdrop.m1v")

	def KeyExit(self):
		if self.inSeries is True:
			if self.isVisible == False:
				self.visibility()
				return
		
			self.showiframe.finishStillPicture()

			self.close()
		elif self.inEpisode is True or self.inSeasons is True:
			self.inSeries = True
			self.inSeasons = False
			self.inEpisode = False
			self["listview"].setList(self.serieslist)
			self["listview"].setIndex(self.rememeberSeriesIndex)
			self.refresh()

#------------------------------------------------------------------------------------------


