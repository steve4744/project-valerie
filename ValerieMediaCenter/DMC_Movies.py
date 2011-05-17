# -*- coding: utf-8 -*-

import gettext
import math
import os
from   os import environ

from enigma import getDesktop
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import *
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.ChoiceBox import ChoiceBox
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, SCOPE_LANGUAGE

from DataElement import DataElement
from DMC_Global import Showiframe, getAPILevel
from DMC_Player import PVMC_Player

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin, registerPlugin

from DatabaseLayer import databaseLayer
#------------------------------------------------------------------------------------------

def localeInit():
	lang = language.getLanguage()
	environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ProjectValerie", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ProjectValerie/locale/"))

def _(txt):
	t = gettext.dgettext("ProjectValerie", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
#------------------------------------------------------------------------------------------

class PVMC_Movies(Screen, HelpableScreen):

	# API Levels:
	# 1 - Initial Level
	# 2 - Big Changes which are introduced with the blueSky skin
	# 3 - Introduces resolution dependend poster

	ShowStillPicture = False

	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.showiframe = Showiframe()
		
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		
		self.APILevel = 1 
		try:
			self.APILevel = int(DataElement().getDataPreloading(self, "API"))
		except Exception, ex:
			printl(str(ex))
			self.APILevel = 1
		
		printl("APILevel=" + str(self.APILevel))
		
		if self.APILevel >= 2:
			self["API"] = DataElement()
		
		self.isVisible = True
		self.moviedb = {}
		self.genreFilter = ""
		self.Sort = ""
		
		list = []
		
		if self.APILevel == 1:
			self["listview"] = MenuList(list)
		elif self.APILevel >= 2:
			self["listview"] = List(list, True)
		self["title"] = Label()
		if self.APILevel == 1:
			self["otitle"] = Label()
		self["tag"] = Label()
		self["poster"] = Pixmap()
		self["shortDescription"] = Label()
		if self.APILevel == 1:
			self["director"] = Label()
			self["writer"] = Label()
		self["genre"] = Label()
		self["year"] = Label()
		self["runtime"] = Label()
		
		if self.APILevel >= 2:
			self["total"] = Label()
			self["current"] = Label()
		
		self["key_red"] = StaticText(_("Sort"))
		self["key_green"] = StaticText(_(" "))
		self["key_yellow"] = StaticText(_(" "))
		self["key_blue"] = StaticText(_("Categories"))
		
		try:
			from StillPicture import StillPicture
			self["backdrop"] = StillPicture(session)
			self.ShowStillPicture = True
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		if self.APILevel >= 2:
			self["listview_itemsperpage"] = DataElement()
		
		self.postersize = ""
		if self.APILevel >= 3:
			dSize = getDesktop(0).size()
			if dSize.width() == 720 and dSize.height() == 576:
				self.postersize = "_110x214"
			elif dSize.width() == 1024 and dSize.height() == 576:
				self.postersize = "_156x214"
			elif dSize.width() == 1280 and dSize.height() == 720:
				self.postersize = "_195x267"

		for i in range(10):
			stars = "star" + str(i)
			#printl("stars: " + stars, self)
			self[stars] = Pixmap()
			if self[stars].instance is not None:
				self[stars].instance.hide()

		for i in range(10):
			stars = "nostar" + str(i)
			#printl("stars: " + stars, self)
			self[stars] = Pixmap()
		
		self.backdropquality = ""
		if config.plugins.pvmc.backdropquality.value == "Low":
			self.backdropquality = "_low"
		
		#if os.path.exists(u"/hdd/valerie/movies.txd"):
		#		self.USE_DB_VERSION = self.DB_TXD
				
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
				"blue": (self.KeyGenres, _("Categories")),
				"red": (self.KeySort, _("Sort")),
				"stop": (self.leaveMoviePlayer, "Stop Playback"),
				"info": (self.KeyInfo, "show Plot"),
				"menu": (self.KeyPlugins, "show Plugins"),
			}, -2)
		
		# Create Database Layer
		self.db = databaseLayer()
		self.moviedb = self.db.loadMovies()
		#for counter in range (0, len(self.moviedb)):
		#	printl("moviedb rec " + str(counter))
		
		self.reloadMovies()
		
		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.refresh)

	def setCustomTitle(self):
		self.setTitle(_("movies"))

	FAST_STILLPIC = False
	
	def sortList(self,x, y):
		if self.moviedb[x[1]][self.Sort]>self.moviedb[y[1]][self.Sort]:
			return 1
		elif self.moviedb[x[1]][self.Sort]==self.moviedb[y[1]][self.Sort]:
			return 0
		else: # x<y
			return -1

	def reloadMovies(self):
		printl("->", self)
		list =[]
		for key in self.moviedb.keys():
			if self.genreFilter == "" or self.genreFilter in self.moviedb[key]["Genres"]:
				list.append(("  " + self.moviedb[key]["Title"], key, "", "45"))
		
		if self.Sort == "":
			list.sort()
		else:
			list.sort(key=lambda x:self.moviedb[x[1]][self.Sort], reverse=True)
		self["listview"].setList(list)
		if self.APILevel >= 2:
			self["listview"].setIndex(0)
		self.refresh()
		printl("<-", self)

	#def getAvailGenres(self):
	#	return self.AvailableGenresList

	def setText(self, name, value, ignore=False, what=None):
		try:
			if self[name]:
				if len(value) > 0:
					self[name].setText(value)
				elif ignore is False:
					if what is None:
						self[name].setText(_("Not available"))
					else:
						self[name].setText(what + ' ' + _("not available"))
				else:
					self[name].setText(" ")
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def refresh(self, changeBackdrop=True):
		selection = self["listview"].getCurrent()
		printl("selection:" + str(selection), self)
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
				if os.access("/hdd/valerie/media/" + selection[1] + "_poster" + self.postersize + ".png", os.F_OK):
					self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + selection[1] + "_poster" + self.postersize + ".png")
				#Fallback for old skins
				elif len(self.postersize) == 0 and os.access("/hdd/valerie/media/" + selection[1] + "_poster_156x214.png", os.F_OK):
					self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + selection[1] + "_poster_156x214.png")
				else:
					self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/defaultposter" + self.postersize + ".png")
			
			self.setText("title", selection[0])
			if self.APILevel == 1:
				self.setText("otitle", "---")
			
			self.setText("tag", self.moviedb[selection[1]]["Tag"], True)
			self.setText("shortDescription", self.moviedb[selection[1]]["Plot"], what=_("Overview"))
			
			if self.APILevel == 1:
				if self.moviedb[selection[1]].has_key("Directors"):
					self.setText("director", self.moviedb[selection[1]]["Directors"])
				if self.moviedb[selection[1]].has_key("Writers"):
					self.setText("writer", self.moviedb[selection[1]]["Writers"])
			
			self.setText("genre", self.moviedb[selection[1]]["Genres"].replace('|', ", "), what=_("Genre"))
			sele = self.moviedb[selection[1]]
			date = str(sele["Year"])
			if sele.has_key("Month") and sele.has_key("Day"):
				if sele["Month"] > 0 and sele["Day"] > 0:
					date = "%04d-%02d-%02d" % (sele["Year"], sele["Month"], sele["Day"], )
			self.setText("year", date)
			self.setText("runtime", self.moviedb[selection[1]]["Runtime"] + ' ' + _("min"))
			
			if self.APILevel >= 2:
				itemsPerPage = int(self["listview_itemsperpage"].getData())
				itemsTotal = self["listview"].count()
				#print "itemsPerPage", itemsPerPage
				pageTotal = int(math.ceil((itemsTotal / itemsPerPage) + 0.5))
				pageCurrent = int(math.ceil((self["listview"].getIndex() / itemsPerPage) + 0.5))
				self.setText("total", _("Total movies:") + ' ' + str(itemsTotal))
				self.setText("current", _("Pages:") + ' ' + str(pageCurrent) + "/" + str(pageTotal))
			
			for i in range(int(self.moviedb[selection[1]]["Popularity"])):
				if self["star" + str(i)].instance is not None:
					self["star" + str(i)].instance.show()
			
			for i in range(10 - int(self.moviedb[selection[1]]["Popularity"])):
				if self["star" + str(9 - i)].instance is not None:
					self["star" + str(9 - i)].instance.hide()

	def up(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def up_first(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def up_quick(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].up()
		elif self.APILevel >= 2:
			self["listview"].selectPrevious()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def down(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def down_first(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def down_quick(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].down()
		elif self.APILevel >= 2:
			self["listview"].selectNext()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def leftUp(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].pageUp()
		elif self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			index = self["listview"].getIndex() - itemsPerPage
			if index < 0:
				index = 0
			self["listview"].setIndex(index)
		self.refresh()

	def rightDown(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].pageDown()
		elif self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			index = self["listview"].getIndex() + itemsPerPage
			if index >= itemsTotal:
				index = itemsTotal - 1
			self["listview"].setIndex(index)
		self.refresh()

	def KeyOk(self):
		printl("", self)
		if self.isVisible == False:
			self.visibility()
			return
		
		selection = self["listview"].getCurrent()
		if selection is not None:
			playbackPath = self.moviedb[selection[1]]["Path"]
			if os.path.isfile(playbackPath):
				self.showiframe.finishStillPicture()
				
				args = {}
				args["title"] = self.moviedb[selection[1]]["Title"]
				args["year"] = self.moviedb[selection[1]]["Year"]
				args["imdbid"] = self.moviedb[selection[1]]["ImdbId"]
				args["status"] = "playing"
				args["type"] = "movie"
				plugins = getPlugins(where=Plugin.INFO_PLAYBACK)
				for plugin in plugins:
					pluginSettingsList = plugin.fnc(args)
				
				isDVD = False
				dvdFilelist = [ ]
				dvdDevice = None
				
				if self.moviedb[selection[1]]["Path"].lower().endswith(u"ifo"): # DVD
					isDVD = True
					dvdFilelist.append(str(self.moviedb[selection[1]]["Path"].replace(u"/VIDEO_TS.IFO", "").strip()))
				elif self.moviedb[selection[1]]["Path"].lower().endswith(u"iso"): # DVD
					isDVD = True
					dvdFilelist.append(self.moviedb[selection[1]]["Path"])
				
				if isDVD:
					try:
						from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer
						# when iso -> filelist, when folder -> device
						self.session.openWithCallback(self.leaveMoviePlayer, DVDPlayer, dvd_device = dvdDevice, dvd_filelist = dvdFilelist)
					except Exception, ex:
						printl("Exception: " + str(ex), self)
				else:
					playbackList = []
					playbackList.append( (self.moviedb[selection[1]]["Path"], self.moviedb[selection[1]]["Title"]), )
					
					printl("playbackList: " + str(playbackList), self)
					
					self.session.openWithCallback(self.leaveMoviePlayer, PVMC_Player, playbackList)
			else:
				self.session.open(MessageBox, "Not found!\n" + self.moviedb[selection[1]]["Path"] + "\n\nPlease make sure that your drive is connected/mounted.", type = MessageBox.TYPE_ERROR)
		

	def leaveMoviePlayer(self):
		args = {}
		args["status"] = "stopped"
		plugins = getPlugins(where=Plugin.INFO_PLAYBACK)
		for plugin in plugins:
			pluginSettingsList = plugin.fnc(args) 
		
		self.session.nav.playService(None) 
		self.refresh()

	def KeyGenres(self):		
		menu = self.db.getAvailGenres()
		self.session.openWithCallback(self.genresCallback, ChoiceBox, title=_("Select Category"), list = menu)

	def genresCallback(self, choice):
		if choice is None:
			return
		
		if choice[1] == "all":
			self.genreFilter = ""
		else:
			self.genreFilter = choice[1]
		self.reloadMovies()

	def KeySort(self):
		menu = []
		menu.append((_("Title"), "Title"))
		menu.append((_("Aired"), "Year"))
		menu.append((_("Creation"), "Creation"))
		menu.append((_("Popularity"), "Popularity"))
		self.session.openWithCallback(self.sortCallback, ChoiceBox, title=_("Sort by"), list=menu)

	def sortCallback(self, choice):
		if choice is None:
			return

		if choice[1] == "Title":
			self.Sort = ""
		else:
			self.Sort = choice[1]
		self.reloadMovies()

	def Exit(self):
		if self.isVisible == False:
			self.visibility()
			return
		
#		finishStillPicture()
		self.showiframe.finishStillPicture()
		
		self.close()

	class PVMC_MessageBoxInfo(MessageBox):
		def __init__(self, session, title, plot):
			text = _("Title: ") + title + _("\n\nPlot:\n") + plot
			MessageBox.__init__(self, session, text, type = MessageBox.TYPE_INFO)
			
			self.APILevel = getAPILevel(self)
			printl("APILevel=" + str(self.APILevel), self)
			if self.APILevel >= 2:
				self["API"] = DataElement()
			
			if self.APILevel == 1:
				self.skinName = "MessageBox"
			
			self.onLayoutFinish.append(self.setCustomTitle)

		def setCustomTitle(self):
			self.setTitle(_("details"))

	def KeyInfo(self):
		selection = self["listview"].getCurrent()
		if selection is not None:
			self.session.open(self.PVMC_MessageBoxInfo, self.moviedb[selection[1]]["Title"], self.moviedb[selection[1]]["Plot"])
			#self.session.open(MessageBox, _("Title:\n") + self.moviedb[selection[1]]["Title"] + _("\n\nPlot:\n") + self.moviedb[selection[1]]["Plot"], type = MessageBox.TYPE_INFO)

	def KeyPlugins(self):
		pluginList = []
		plugins = getPlugins(where=Plugin.MENU_MOVIES_PLUGINS)
		for plugin in plugins:
			pluginList.append((plugin.name, plugin.start, ))
		
		if len(pluginList) == 0:
			pluginList.append((_("No plugins available"), None, ))
		
		self.session.openWithCallback(self.KeyPluginsConfirmed, ChoiceBox, title=_("Plugins available"), list=pluginList)

	def KeyPluginsConfirmed(self, choice):
		if choice is None or choice[1] is None:
			return
		
		selection = self["listview"].getCurrent()
		if selection is not None and type(selection) != bool:
			self.session.open(choice[1], self.moviedb[selection[1]])

registerPlugin(Plugin(name=_("Movies"), start=PVMC_Movies, where=Plugin.MENU_VIDEOS))
