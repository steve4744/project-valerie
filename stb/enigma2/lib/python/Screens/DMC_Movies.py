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
from Components.ServiceEventTracker import ServiceEventTracker

from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *

from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
from Screens.InfoBar import MoviePlayer
from Plugins.Plugin import PluginDescriptor

from enigma import eStillPicture
from Components.MenuList import MenuList

import os
from os import path as os_path

def getAspect():
	val = AVSwitch().getAspectRatioSetting()
	return val/2

#------------------------------------------------------------------------------------------

class DMC_Movies(Screen, HelpableScreen):

	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.isVisible = True
		list = []
		self.moviedb = {}

		filter = []
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
					self.moviedb[d["ImdbId"]] = d
					list.append((d["Title"], d["ImdbId"], "menu_globalsettings", "50"))
			

		except OSError, e: 
			print "OSError: ", e

		list.sort()

		self["listview"] = MenuList(list)

		self["title"] = Label()
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


		
		self["actions"] = HelpableActionMap(self, "MC_AudioPlayerActions", 
			{
				"ok": (self.KeyOk, "Play selected file"),
				"cancel": (self.Exit, "Exit Audio Player"),
				"left": (self.leftUp, "List Top"),
				"right": (self.rightDown, "List Bottom"),
				"up": (self.up, "List up"),
				"down": (self.down, "List down"),
			}, -2)

		eStillPicture.getInstance().showSinglePic("/hdd/valerie/media/tt" + list[0][1] + "_backdrop.m1v")
		#self["poster"].setPixmapFromFile("/hdd/valerie/media/tt" + selection[1] + "_poster.png")
		self["title"].setText(list[0][0])
		self["tag"].setText(self.moviedb[list[0][1]]["Tag"])
		self["shortDescription"].setText(self.moviedb[list[0][1]]["Plot"])
		self["director"].setText(self.moviedb[list[0][1]]["Directors"])
		self["writer"].setText(self.moviedb[list[0][1]]["Writers"])
		self["genre"].setText(self.moviedb[list[0][1]]["Genres"])
		self["year"].setText(self.moviedb[list[0][1]]["Year"])
		self["runtime"].setText(self.moviedb[list[0][1]]["Runtime"])

		#for i in range(int(self.moviedb[list[0][1]]["Popularity"])):
		#	stars = "star" + str(i)
		#	print stars
		#	self["star0"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Screens/MediaCenter/skins/defaultHD/images/Valerie_Star.png")
#
#		for i in range(10 - int(self.moviedb[list[0][1]]["Popularity"])):
#			self["star0"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Screens/MediaCenter/skins/defaultHD/images/Valerie_NoStar.png")
					
	def up(self):
		self["listview"].up()
		selection = self["listview"].getCurrent()
		if selection is not None:
			eStillPicture.getInstance().showSinglePic("/hdd/valerie/media/tt" + selection[1] + "_backdrop.m1v")
			self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/tt" + selection[1] + "_poster.png")
			self["title"].setText(selection[0])
			self["tag"].setText(self.moviedb[selection[1]]["Tag"])
			self["shortDescription"].setText(self.moviedb[selection[1]]["Plot"])
			self["director"].setText(self.moviedb[selection[1]]["Directors"])
			self["writer"].setText(self.moviedb[selection[1]]["Writers"])
			self["genre"].setText(self.moviedb[selection[1]]["Genres"])
			self["year"].setText(self.moviedb[selection[1]]["Year"])
			self["runtime"].setText(self.moviedb[selection[1]]["Runtime"])
			for i in range(int(self.moviedb[selection[1]]["Popularity"])):
				self["star" + str(i)].instance.setPixmapFromFile("/usr/lib/enigma2/python/Screens/MediaCenter/skins/defaultHD/images/Valerie_Star.png")

			for i in range(10 - int(self.moviedb[selection[1]]["Popularity"])):
				self["star" + str(9 - i)].instance.setPixmapFromFile("/usr/lib/enigma2/python/Screens/MediaCenter/skins/defaultHD/images/Valerie_NoStar.png")
#		self.ThumbTimer.start(config.plugins.mc_ap.preview_delay.getValue() * 1000, True)

	def down(self):
		self["listview"].down()
		selection = self["listview"].getCurrent()
		if selection is not None:
			eStillPicture.getInstance().showSinglePic("/hdd/valerie/media/tt" + selection[1] + "_backdrop.m1v")
			self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/tt" + selection[1] + "_poster.png")
			self["title"].setText(selection[0])	
			self["tag"].setText(self.moviedb[selection[1]]["Tag"])	
			self["shortDescription"].setText(self.moviedb[selection[1]]["Plot"])
			self["director"].setText(self.moviedb[selection[1]]["Directors"])
			self["writer"].setText(self.moviedb[selection[1]]["Writers"])
			self["genre"].setText(self.moviedb[selection[1]]["Genres"])
			self["year"].setText(self.moviedb[selection[1]]["Year"])
			self["runtime"].setText(self.moviedb[selection[1]]["Runtime"])
			for i in range(int(self.moviedb[selection[1]]["Popularity"])):
				self["star" + str(i)].instance.setPixmapFromFile("/usr/lib/enigma2/python/Screens/MediaCenter/skins/defaultHD/images/Valerie_Star.png")

			for i in range(10 - int(self.moviedb[selection[1]]["Popularity"])):
				self["star" + str(9 - i)].instance.setPixmapFromFile("/usr/lib/enigma2/python/Screens/MediaCenter/skins/defaultHD/images/Valerie_NoStar.png")
		
	def leftUp(self):
		self["listview"].pageUp()
#		self.ThumbTimer.start(config.plugins.mc_ap.preview_delay.getValue() * 1000, True)
		
	def rightDown(self):
		self["listview"].pageDown()
#		self.ThumbTimer.start(config.plugins.mc_ap.preview_delay.getValue() * 1000, True)



	def KeyOk(self):
		if self.isVisible == False:
			self.visibility()
			return
		
		eStillPicture.getInstance().finishShowSinglePic()
		
		selection = self["listview"].getCurrent()
		if selection is not None:
			self.session.open(MoviePlayer, eServiceReference("4097:0:1:0:0:0:0:0:0:0:" + self.moviedb[selection[1]]["Path"]))

	def Exit(self):
		if self.isVisible == False:
			self.visibility()
			return
		
		eStillPicture.getInstance().finishShowSinglePic()

		self.close()

#------------------------------------------------------------------------------------------

