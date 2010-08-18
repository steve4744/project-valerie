from enigma import eTimer, eWidget, eRect, eServiceReference, iServiceInformation, iPlayableService, ePicLoad
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
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

#------------------------------------------------------------------------------------------

class DMC_Movies(Screen, HelpableScreen, InfoBarBase):

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
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		
		list = []

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


		
		self["actions"] = HelpableActionMap(self, "DMC_AudioPlayerActions", 
			{
				"ok": (self.KeyOk, "Play selected file"),
				"cancel": (self.Exit, "Exit Audio Player"),
				"left": (self.leftUp, "List Top"),
				"right": (self.rightDown, "List Bottom"),
				"up": (self.up, "List up"),
				"down": (self.down, "List down"),
				"blue": (self.KeyGenres, "Genres"),
				"red": (self.KeySort, "Sort"),
			}, -2)
		self["listview"] = MenuList(list)
		self.loadMoviesDB()

		self.onFirstExecBegin.append(self.refresh)

	def sortList(self,x, y):
		if self.moviedb[x[1]][self.Sort]>self.moviedb[y[1]][self.Sort]:
			return 1
		elif self.moviedb[x[1]][self.Sort]==self.moviedb[y[1]][self.Sort]:
			return 0
		else: # x<y
			return -1


	def loadMoviesDB(self):
		filter = []
		list = []
		filter.append("Tag")
		filter.append("Plot")
		filter.append("LocalPlot")
		filter.append("Directors")
		filter.append("Writers")
		filter.append("Genres")
		filter.append("Year")
		filter.append("Runtime")
		filter.append("Popularity")
		filter.append("ImdbId")
		filter.append("Title")
		filter.append("LocalTitle")
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
						print "skipping ", d["LocalTitle"]
						continue
					self.moviedb[d["ImdbId"]] = d
					if d["LocalTitle"] != "" and config.plugins.dmc.uselocal.value == True:
						print "adding ", d["LocalTitle"]
						list.append(("  " + d["LocalTitle"], d["ImdbId"], "menu_globalsettings", "45"))
					else:
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
		self["listview"].moveToIndex(1)
		self.refresh()

	def getAvailGenres(self):
		list = []
		glist = []
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

						if "Genres" in key : 
							gens = text.split(';')
							for gen in gens:
								gen=gen.lstrip().rstrip()
								if not gen in glist:
									glist.append(gen)
									list.append((_(gen), gen))
						
			
		except OSError, e: 
			print "OSError: ", e

		list.sort()
		list.insert(0,(_("All"), "all"))
		return list
		
	def refresh(self):
		selection = self["listview"].getCurrent()
		if selection is not None:
#			showStillpicture("/hdd/valerie/media/tt" + selection[1] + "_backdrop.m1v")
			if os.access("/hdd/valerie/media/" + selection[1] + "_backdrop.m1v", os.F_OK):
				self.showiframe.showStillpicture("/hdd/valerie/media/" + selection[1] + "_backdrop.m1v")
			elif os.access("/hdd/valerie/media/" + selection[1] + "_backdrop.mvi", os.F_OK):
				self.showiframe.showStillpicture("/hdd/valerie/media/" + selection[1] + "_backdrop.mvi")
			else:
				self.showiframe.showStillpicture("/hdd/valerie/media/defaultbackdrop.m1v")
			self["title"].setText(selection[0])
			self["otitle"].setText(self.moviedb[selection[1]]["Title"])
			self["tag"].setText(self.moviedb[selection[1]]["Tag"])
			if self.moviedb[selection[1]]["LocalPlot"]!="" and config.plugins.dmc.uselocal.value == True:
				self["shortDescription"].setText(self.moviedb[selection[1]]["LocalPlot"])
			else:
				self["shortDescription"].setText(self.moviedb[selection[1]]["Plot"])
			if self.moviedb[selection[1]].has_key("Directors"):
				self["director"].setText(self.moviedb[selection[1]]["Directors"])
			if self.moviedb[selection[1]].has_key("Writers"):
				self["writer"].setText(self.moviedb[selection[1]]["Writers"])
			self["genre"].setText(self.moviedb[selection[1]]["Genres"])
			self["year"].setText(self.moviedb[selection[1]]["Year"])
			self["runtime"].setText(self.moviedb[selection[1]]["Runtime"])
			if self["poster"].instance is not None:
				if os.access("/hdd/valerie/media/" + selection[1] + "_poster.png", os.F_OK):
					self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + selection[1] + "_poster.png")
				else:
					self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/defaultposter.png")

			for i in range(int(self.moviedb[selection[1]]["Popularity"])):
				if self["star" + str(i)].instance is not None:
					self["star" + str(i)].instance.show()

			for i in range(10 - int(self.moviedb[selection[1]]["Popularity"])):
				if self["star" + str(9 - i)].instance is not None:
					self["star" + str(9 - i)].instance.hide()

	def up(self):
		self["listview"].up()
		self.refresh()
		

	def down(self):
		self["listview"].down()
		self.refresh()
		
	def leftUp(self):
		self["listview"].pageUp()
		self.refresh()
		
	def rightDown(self):
		self["listview"].pageDown()
		self.refresh()


	def KeyOk(self):
		if self.isVisible == False:
			self.visibility()
			return
		
		selection = self["listview"].getCurrent()
		if selection is not None:
			if os.path.isfile(self.moviedb[selection[1]]["Path"]):
				self.showiframe.finishStillPicture()
				self.session.openWithCallback(self.leaveMoviePlayer, MoviePlayer, eServiceReference("4097:0:1:0:0:0:0:0:0:0:" + self.moviedb[selection[1]]["Path"]))
			else:
				self.session.open(MessageBox, "Not found!\n" + self.moviedb[selection[1]]["Path"] + "\n\nPlease make sure that your drive is connected/mounted.", type = MessageBox.TYPE_ERROR)
		

	def leaveMoviePlayer(self): 
		self.session.nav.playService(None) 
		selection = self["listview"].getCurrent()
		if selection is not None:
#			showStillpicture("/hdd/valerie/media/tt" + selection[1] + "_backdrop.m1v")
			if os.access("/hdd/valerie/media/tt" + selection[1] + "_backdrop.m1v", os.F_OK):
				self.showiframe.showStillpicture("/hdd/valerie/media/tt" + selection[1] + "_backdrop.m1v")
			else:
				self.showiframe.showStillpicture("/hdd/valerie/media/defaultbackdrop.m1v")

	def KeyGenres(self):
		menu=self.getAvailGenres()
		self.session.openWithCallback(self.genresCallback, ChoiceBox, title="Select Genre", list=menu)

	def genresCallback(self, choice):
		if choice is None:
			return

		if choice[1] == "all":
			self.genreFilter = ""
		else:
			self.genreFilter = choice[1]
		self.loadMoviesDB()
		
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
		self.loadMoviesDB()

	def Exit(self):
		if self.isVisible == False:
			self.visibility()
			return
		
#		finishStillPicture()
		self.showiframe.finishStillPicture()

		self.close()

#------------------------------------------------------------------------------------------
