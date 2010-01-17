from enigma import eTimer, eDVBDB, getDesktop
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText

from Components.ConfigList import ConfigList
from Components.config import *

from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch

import os

# Plugins
from MC_AudioPlayer import MC_AudioPlayer
from MC_VideoPlayer import MC_VideoPlayer
from DMC_Movies import DMC_Movies
from DMC_Series import DMC_Series
from MC_Settings import MC_Settings, MCS_Update


from Components.MenuList import MenuList
from DMC_Global import printl

# Unfortunaly not everyone has twisted installed ...
try:
	from twisted.web.client import getPage
except Exception, e:
	printl("import twisted.web.client failed")

#------------------------------------------------------------------------------------------
	
class DMC_MainMenu(Screen):
	def __init__(self, session):
		printl("DMC_MainMenu:__init__")
		Screen.__init__(self, session)

		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()

	
		list = []
		list.append(("Movies", "DMC_Watch", "menu_watch", "50"))
		list.append(("TV", "InfoBar", "menu_tv", "50"))
		#list.append(("TV", "Exit", "menu_exit", "50"))
		list.append(("Settings", "MC_Settings", "menu_settings", "50"))
		list.append(("Pictures", "MC_PictureViewer", "menu_pictures", "50"))
		list.append(("Music", "MC_AudioPlayer", "menu_music", "50"))
		#list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list, True)

		listWatch = []
		listWatch.append((" ", "dummy", "menu_dummy", "50"))
		listWatch.append(("Movies", "DMC_Movies", "menu_movies", "50"))
		listWatch.append(("Series", "DMC_Series", "menu_series", "50"))
		listWatch.append(("Series", "MC_VideoPlayer", "menu_watch_all", "50"))
		self["menuWatch"] = List(listWatch, True)
		self.Watch = False

		self["title"] = StaticText("")
		self["welcomemessage"] = StaticText("")

		#self["moveWatchMovies"] = MovingPixmap()
		#self["moveWatchSeries"] = MovingPixmap()

		self.inter = 0

		self["actions"] = HelpableActionMap(self, "DMC_MainMenuActions", 
			{
				"ok": self.okbuttonClick,
				"cancel": self.cancel,
				"left": self.left,
				"right": self.right,
				"up": self.up,
				"down": self.down,
			}, -1)

		if config.plugins.dmc.checkforupdate.value == True:
			self.onFirstExecBegin.append(self.checkForUpdate)


	def checkForUpdate(self):
		self.url = config.plugins.dmc.url.value + config.plugins.dmc.updatexml.value
		printl("Checking URL: " + self.url) 
		try:
			getPage(self.url).addCallback(self.gotUpdateInformation).addErrback(self.Error)
		except Exception, e:
			printl("""Could not download HTTP Page (%s)""" % e)

	def gotUpdateInformation(self, html):
		printl(str(html))
		tmp_infolines = html.splitlines()     
		remoteversion = int(tmp_infolines[0])

		if config.plugins.dmc.version.value < remoteversion:
			self.session.openWithCallback(self.startUpdate, MessageBox,_("""A new version of MediaCenter is available for download!\n\nVersion: %s""" % remoteversion), MessageBox.TYPE_INFO)

	def startUpdate(self, answer):
		if answer is True:
			printl("Updating not yet supported!")
			#self.session.open(MCS_Update)

	def Error(self, error):
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)

	def okbuttonClick(self):
		print "okbuttonClick"

		if self.Watch == True:
			selection = self["menuWatch"].getCurrent()
			if selection is not None:
				if selection[1] == "DMC_Movies":
					self.session.open(DMC_Movies)
				elif selection[1] == "DMC_Series":
					self.session.open(DMC_Series)
				elif selection[1] == "MC_VideoPlayer":
					self.session.open(MC_VideoPlayer)
		else:
			selection = self["menu"].getCurrent()
			if selection is not None:
				if selection[1] == "DMC_Watch":
					self["menuWatch"].setIndex(2)
					self.Watch = True;
				elif selection[1] == "MC_AudioPlayer":
					self.session.open(MC_AudioPlayer)
				elif selection[1] == "MC_Settings":
					from Menu import MainMenu, mdom
					menu = mdom.getroot()
					assert menu.tag == "menu", "root element in menu must be 'menu'!"


					self.session.open(MainMenu, menu)
				elif selection[1] == "InfoBar":
					self.Exit()
					#eDVBDB.getInstance().reloadBouquets()
					#from Screens.InfoBar import InfoBar
					#self.session.open(InfoBar)
				elif selection[1] == "Exit":
					self.Exit()

	def up(self):
		self.cancel()
		return

	def down(self):
		self.okbuttonClick()
		return

	def right(self):
		if self.Watch == True:
			self["menuWatch"].selectNext()
			if self["menuWatch"].getIndex() == 0:
				self["menuWatch"].selectNext()
		else:
			self["menu"].selectNext()

	def left(self):
		if self.Watch == True:
			self["menuWatch"].selectPrevious()
			if self["menuWatch"].getIndex() == 0:
				self["menuWatch"].selectPrevious()
		else:
			self["menu"].selectPrevious()

	def cancel(self):
		if self.Watch == True:
			self["menuWatch"].setIndex(0)
			self.Watch = False;

		return

	def Exit(self):
		self.close()

