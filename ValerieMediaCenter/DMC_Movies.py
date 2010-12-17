from enigma import eTimer, eWidget, eRect, eServiceReference, iServiceInformation, iPlayableService, ePicLoad
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
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
from Screens.InfoBar import MoviePlayer

from Plugins.Plugin import PluginDescriptor

#from enigma import eStillPicture
from Components.MenuList import MenuList

import os
from os import path as os_path

def getAspect():
	val = AVSwitch().getAspectRatioSetting()
	return val/2

from DMC_Global import Showiframe
from DMC_Player import PVMC_Player 
from DataElement import DataElement
import math
#------------------------------------------------------------------------------------------

class PVMC_Movies(Screen, HelpableScreen, InfoBarBase):

	def __init__(self, session):
		Screen.__init__(self, session)
		InfoBarBase.__init__(self)
		HelpableScreen.__init__(self)
		self.showiframe = Showiframe()

		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()		

		self.isVisible = True
		self.moviedb = {}
		self.genreFilter = ""
		self.Sort = ""
		
		list = []

		self["listview"] = List(list, True)
		self["title"] = Label()
		self["otitle"] = Label()
		self["tag"] = Label()
		self["poster"] = Pixmap()
		self["shortDescription"] = Label()
		self["director"] = Label()
		self["writer"] = Label()
		self["genre"] = Label()
		self["year"] = Label()
		self["runtime"] = Label()
		
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
		
		if os.path.exists(u"/hdd/valerie/movies.txd"):
				self.USE_DB_VERSION = self.DB_TXD
		
		self["actions"] = HelpableActionMap(self, "PVMC_AudioPlayerActions", 
			{
				"ok": (self.KeyOk, "Play selected file"),
				"cancel": (self.Exit, "Exit Audio Player"),
				"left": (self.leftUp, "List Top"),
				"right": (self.rightDown, "List Bottom"),
				"up": (self.up, "List up"),
				"down": (self.down, "List down"),
				"up_quick": (self.up_quick, "List up"),
				"down_quick": (self.down_quick, "List down"),
				"blue": (self.KeyGenres, "Genres"),
				"red": (self.KeySort, "Sort"),
				"stop": (self.leaveMoviePlayer, "Stop Playback"),
			}, -2)
		
		self.loadMovies()
		
		self.onFirstExecBegin.append(self.refresh)

	DB_TXT = 1
	DB_TXD = 2
	DB_PICKLE = 3
	DB_SQLITE= 4
	USE_DB_VERSION = DB_TXT

	FAST_STILLPIC = False

	def sortList(self,x, y):
		if self.moviedb[x[1]][self.Sort]>self.moviedb[y[1]][self.Sort]:
			return 1
		elif self.moviedb[x[1]][self.Sort]==self.moviedb[y[1]][self.Sort]:
			return 0
		else: # x<y
			return -1

	def loadMovies(self):
		if self.USE_DB_VERSION == self.DB_TXT:
			self.loadMoviesDB()
		elif self.USE_DB_VERSION == self.DB_TXD:
			self.loadMoviesTxd()

	def loadMoviesTxd(self):
		list =[]
		try:
			self.serieslist=[]
			db = open("/hdd/valerie/movies.txd").read()[:-1]
			
			lines = db.split("\n")
			version = lines[0]
			linesLen = len(lines)
			print "Lines:", linesLen
			for i in range(1, linesLen, 11):
				if lines[i+0] == "EOF":
					break
				d = {} 
				d["ImdbId"]    = lines[i+0]
				d["Title"]     = lines[i+1]
				d["Tag"]       = lines[i+2]
				d["Year"]      = int(lines[i+3])
				
				d["Path"] = lines[i+4] + "/" + lines[i+5] + "." + lines[i+6]
				
				d["Plot"]       = lines[i+7]
				d["Runtime"]    = lines[i+8]
				d["Popularity"] = lines[i+9]
				
				d["Genres"] = lines[i+10]
				
				# deprecated
				d["Directors"] = ""
				d["Writers"]   = ""
				d["OTitle"]    = ""
				
				if self.genreFilter != "" and d["Genres"] != "" and not self.genreFilter in d["Genres"]:
					print "skipping ", d["Title"]
					continue
				self.moviedb[d["ImdbId"]] = d
	
				print "adding ", d["Title"]
				list.append(("  " + d["Title"], d["ImdbId"], "menu_globalsettings", "45"))
		
		except OSError, e: 
			print "OSError: ", e
		except IOError, e: 
			print "OSError: ", e
		
		if self.Sort == "":
			list.sort()
		else:
			list.sort(self.sortList,reverse=True)
		self["listview"].setList(list)
		self["listview"].setIndex(0)
		self.refresh()

	def loadMoviesDB(self):
		filter = []
		list = []
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
		filter.append("Path")
		
		try:
			db = open("/hdd/valerie/moviedb.txt").read()[:-1]
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

					#print d
					if self.genreFilter != "" and d["Genres"] != "" and not self.genreFilter in d["Genres"]:
						print "skipping ", d["Title"]
						continue
					self.moviedb[d["ImdbId"]] = d

					print "adding ", d["Title"]
					list.append(("  " + d["Title"], d["ImdbId"], "menu_globalsettings", "45"))
		
		except OSError, e: 
			print "OSError: ", e
		except IOError, e: 
			print "OSError: ", e
		
		if self.Sort == "":
			list.sort()
		else:
			list.sort(self.sortList, reverse=True)
		self["listview"].setList(list)
		self["listview"].setIndex(0)
		self.refresh()

	def getAvailGenres(self):
		list = []
		for movie in self.moviedb.values():
			genres = movie["Genres"]
			for genre in genres.split("|"):
				if len(genre) > 0 and (_(genre), genre) not in list:
					list.append((_(genre), genre))

		list.sort()
		list.insert(0,(_("All"), "all"))
		return list

	def setText(self, name, value, ignore=False):
		try:
			if self[name]:
				if len(value) > 0:
					self[name].setText(value)
				elif ignore is False:
					self[name].setText("Not available")
				else:
					self[name].setText(" ")
		except Exception, ex:
			print "setText::", ex

	def refresh(self, changeBackdrop=True):
		selection = self["listview"].getCurrent()
		print "SELECTION", selection
		if selection is not None and type(selection) != bool:
			if changeBackdrop is True:
				if self.ShowStillPicture is True:
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
			self.setText("otitle", "---")
			
			self.setText("tag", self.moviedb[selection[1]]["Tag"], True)
			self.setText("shortDescription", self.moviedb[selection[1]]["Plot"])
			
			if self.moviedb[selection[1]].has_key("Directors"):
				self.setText("director", self.moviedb[selection[1]]["Directors"])
			if self.moviedb[selection[1]].has_key("Writers"):
				self.setText("writer", self.moviedb[selection[1]]["Writers"])
			
			self.setText("genre", self.moviedb[selection[1]]["Genres"].replace('|', ", "))
			self.setText("year", str(self.moviedb[selection[1]]["Year"]))
			self.setText("runtime", self.moviedb[selection[1]]["Runtime"] + " min")
			
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			#print "itemsPerPage", itemsPerPage
			pageTotal = int(math.ceil((itemsTotal / itemsPerPage) + 0.5))
			pageCurrent = int(math.ceil((self["listview"].getIndex() / itemsPerPage) + 0.5))
			self.setText("total", "Total movies: " + str(itemsTotal))
			self.setText("current", str(pageCurrent) + "/" + str(pageTotal))
			
			for i in range(int(self.moviedb[selection[1]]["Popularity"])):
				if self["star" + str(i)].instance is not None:
					self["star" + str(i)].instance.show()

			for i in range(10 - int(self.moviedb[selection[1]]["Popularity"])):
				if self["star" + str(9 - i)].instance is not None:
					self["star" + str(9 - i)].instance.hide()

	def up(self):
		print "PVMC_Movies::up"
		#self["listview"].up()
		if self.FAST_STILLPIC is False:
			self.refresh()

	def up_first(self):
		print "PVMC_Movies::up_first"
		#self["listview"].up()
		if self.FAST_STILLPIC is False:
			self.refresh()

	def up_quick(self):
		print "PVMC_Movies::up_quick"
		self["listview"].selectPrevious()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def down(self):
		print "PVMC_Movies::down"
		#self["listview"].down()
		if self.FAST_STILLPIC is False:
			self.refresh()

	def down_first(self):
		print "PVMC_Movies::down_first"
		#self["listview"].down()
		if self.FAST_STILLPIC is False:
			self.refresh()

	def down_quick(self):
		print "PVMC_Movies::down_quick"
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


	def KeyOk(self):
		if self.isVisible == False:
			self.visibility()
			return
		
		selection = self["listview"].getCurrent()
		if selection is not None:
			playbackPath = self.moviedb[selection[1]]["Path"]
			if os.path.isfile(playbackPath):
				self.showiframe.finishStillPicture()
				
				playbackList = []
				playbackList.append( (self.moviedb[selection[1]]["Path"], self.moviedb[selection[1]]["Title"]), )
				
				print "PLAYBACK: ", playbackList
				self.session.openWithCallback(self.leaveMoviePlayer, PVMC_Player, playbackList)
			else:
				self.session.open(MessageBox, "Not found!\n" + self.moviedb[selection[1]]["Path"] + "\n\nPlease make sure that your drive is connected/mounted.", type = MessageBox.TYPE_ERROR)
		

	def leaveMoviePlayer(self): 
		self.session.nav.playService(None) 
		selection = self["listview"].getCurrent()
		if selection is not None:
			if os.access("/hdd/valerie/media/tt" + selection[1] + "_backdrop" + self.backdropquality + ".m1v", os.F_OK):
				self.showiframe.showStillpicture("/hdd/valerie/media/tt" + selection[1] + "_backdrop" + self.backdropquality + ".m1v")
			else:
				self.showiframe.showStillpicture("/hdd/valerie/media/defaultbackdrop.m1v")

	def KeyGenres(self):
		menu = self.getAvailGenres()
		self.session.openWithCallback(self.genresCallback, ChoiceBox, title="Select Genre", list = menu)

	def genresCallback(self, choice):
		if choice is None:
			return

		if choice[1] == "all":
			self.genreFilter = ""
		else:
			self.genreFilter = choice[1]
		self.loadMovies()
		
	def KeySort(self):
		menu = []
		menu.append((_("Title"), "title"))
		menu.append((_("Year"), "Year"))
		menu.append((_("Popularity"), "Popularity"))
		self.session.openWithCallback(self.sortCallback, ChoiceBox, title="Sort by", list=menu)

	def sortCallback(self, choice):
		if choice is None:
			return

		if choice[1] == "title":
			self.Sort = ""
		else:
			self.Sort = choice[1]
		self.loadMovies()

	def Exit(self):
		if self.isVisible == False:
			self.visibility()
			return
		
#		finishStillPicture()
		self.showiframe.finishStillPicture()

		self.close()

#------------------------------------------------------------------------------------------
