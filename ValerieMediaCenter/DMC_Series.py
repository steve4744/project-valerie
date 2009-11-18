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
#from Screens.DMC_MoviePlayer import DMC_MoviePlayer
from Screens.InfoBar import MoviePlayer

from Plugins.Plugin import PluginDescriptor


from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap

import os
from os import path as os_path

hasBuildInStillpicture = True

try:
	from enigma import eStillPicture
except Exception, e:
	print "No build in Stillpicture support!"
	hasBuildInStillpicture = False

def finishStillPicture():
	if not hasBuildInStillpicture:
		os.system("killall showiframe")
		

def showStillpicture(picture):
	if not os.path.exists(picture):
		picture="/boot/bootlogo.mvi"
	if hasBuildInStillpicture:
		eStillPicture.getInstance().showSinglePic(picture)
	else:
		finishStillPicture()
		os.system("/usr/bin/showiframe " + picture + " &")

#------------------------------------------------------------------------------------------

class DMC_Series(Screen, HelpableScreen, InfoBarBase):

	def __init__(self, session):
		Screen.__init__(self, session)
		InfoBarBase.__init__(self)
		HelpableScreen.__init__(self)
		
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()	

		self.isVisible = True
		self.inSeries = True
		self.inSeasons = False
		self.inEpisode = False
		self.rememeberSeriesIndex = 0
		self.serieslist = []
		self.moviedb = {}
		self.selectedSeries = 0

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
		filter.append("TheTvDb")

		try:
			db = open("/hdd/valerie/seriesdb.txt").read()[:-1]
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
					self.moviedb[d["TheTvDb"]] = d
					self.serieslist.append((d["Title"], d["TheTvDb"], "menu_globalsettings", "50"))
			
		except OSError, e: 
			print "OSError: ", e

		self.serieslist.sort()

		self["listview"] = MenuList(self.serieslist)

		for i in range(10):
			stars = "star" + str(i)
			print stars
			self[stars] = Pixmap()


		
		self["actions"] = HelpableActionMap(self, "MC_AudioPlayerActions", 
			{
				"ok": (self.KeyOk, "Play selected file"),
				"cancel": (self.KeyExit, "Exit Audio Player"),
				"left": (self.leftUp, "List Top"),
				"right": (self.rightDown, "List Bottom"),
				"up": (self.up, "List up"),
				"down": (self.down, "List down"),
			}, -2)

		self["poster"] 				= Pixmap()

		print "count: ", self.serieslist.count
		if self.serieslist.count > 0:

			showStillpicture("/hdd/valerie/media/" + self.serieslist[0][1] + "_backdrop.m1v")
			#self["poster"] 				= LoadPixmap("/hdd/valerie/media/" + self.serieslist[0][1] + "_poster.png")
			self["title"] 				= Label(self.serieslist[0][0])
			self["tag"] 				= Label(self.moviedb[self.serieslist[0][1]]["Tag"])
			self["shortDesc"] 	= Label(self.moviedb[self.serieslist[0][1]]["Plot"])
			self["director"] 			= Label(self.moviedb[self.serieslist[0][1]]["Directors"])
			self["writer"] 				= Label(self.moviedb[self.serieslist[0][1]]["Writers"])
			self["genre"] 				= Label(self.moviedb[self.serieslist[0][1]]["Genres"])
			self["year"] 				= Label(self.moviedb[self.serieslist[0][1]]["Year"])
			self["runtime"] 			= Label(self.moviedb[self.serieslist[0][1]]["Runtime"])



			#for i in range(int(self.moviedb[self.serieslist[0][1]]["Popularity"])):
			#	self["star" + str(i)] = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/defaultHD/images/Valerie_Star.png")

			#for i in range(10 - int(self.moviedb[self.serieslist[0][1]]["Popularity"])):
			#	self["star" + str(9 - i)] = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/defaultHD/images/Valerie_NoStar.png")
		else:

			showStillpicture("/hdd/valerie/media/default_backdrop.m1v")
			#self["poster"] 				= Pixmap()
			self["title"] 				= Label("Libary empty!")
			self["tag"] 				= Label("Please setup")
			self["shortDesc"] 	= Label("None")
			self["director"] 			= Label("")
			self["writer"] 				= Label("")
			self["genre"] 				= Label("")
			self["year"] 				= Label("")
			self["runtime"] 			= Label("")

			#for i in range(10):
			#	self["star" + str(i)] = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/defaultHD/images/Valerie_NoStar.png")

		

	def refresh(self):
		selection = self["listview"].getCurrent()
		if selection is not None:
			if self.inSeries is True:
				showStillpicture("/hdd/valerie/media/" + selection[1] + "_backdrop.m1v")
				self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + selection[1] + "_poster.png")
				self["title"].setText(selection[0])
				self["tag"].setText(self.moviedb[selection[1]]["Tag"])
				self["shortDesc"].setText(self.moviedb[selection[1]]["Plot"])
				self["director"].setText(self.moviedb[selection[1]]["Directors"])
				self["writer"].setText(self.moviedb[selection[1]]["Writers"])
				self["genre"].setText(self.moviedb[selection[1]]["Genres"])
				self["year"].setText(self.moviedb[selection[1]]["Year"])
				self["runtime"].setText(self.moviedb[selection[1]]["Runtime"])
				for i in range(int(self.moviedb[selection[1]]["Popularity"])):
					self["star" + str(i)].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/defaultHD/images/Valerie_Star.png")

				for i in range(10 - int(self.moviedb[selection[1]]["Popularity"])):
					self["star" + str(9 - i)].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/defaultHD/images/Valerie_NoStar.png")

			elif self.inEpisode is True:
				self["title"].setText(selection[0])
				self["shortDesc"].setText(self.episodesdb[selection[1]]["Plot"])
			
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

		selection = self["listview"].getCurrent()
		if selection is not None:
			if self.inSeries is True:
				self.inSeries = False
				self.inSeasons = True
				self.inEpisode = False
				
				self.selectedSeries = selection[1]
				self.rememeberSeriesIndex = self["listview"].getSelectionIndex()
				
				seasonslist = []
				self.seasonsdb = {}
				
				filter = []
				filter.append("Season")
				filter.append("Episode")
				
				try:
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

							duplicate = False
							for season in seasonslist:
								print "Season", season
								if d["Season"] is season[1]:
									duplicate = True
							if duplicate is False:
								seasonslist.append(("Season " + d["Season"], d["Season"], "menu_globalsettings", "50"))
			
				except OSError, e: 
					print "OSError: ", e

				seasonslist.sort()
				self["listview"].setList(seasonslist)
				self["listview"].moveToIndex(0)
				self.refresh()
				
			elif self.inSeasons is True:
				self.inSeries = False
				self.inSeasons = False
				self.inEpisode = True

				self.selectedSeason = selection[1]
				self.rememeberSeasonsIndex = self["listview"].getSelectionIndex()

				episodeslist = []
				self.episodesdb = {}

				filter = []
				filter.append("Path")
				filter.append("Plot")
				filter.append("Directors")
				filter.append("Writers")
				filter.append("Genres")
				filter.append("Year")
				filter.append("Runtime")
				filter.append("Popularity")
				filter.append("ImdbId")
				filter.append("Title")
				filter.append("TheTvDb")
				filter.append("Season")
				filter.append("Episode")

				try:
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

							if d["Season"] is self.selectedSeason:
								self.episodesdb[d["Season"]+"x"+ ("%02d" % int(d["Episode"]))] = d
								episodeslist.append((d["Season"]+"x"+("%02d" % int(d["Episode"])) + ": " + d["Title"], d["Season"]+"x"+("%02d" % int(d["Episode"])), "menu_globalsettings", "50"))
			
				except OSError, e: 
					print "OSError: ", e

				episodeslist.sort()
				self["listview"].setList(episodeslist)
				self["listview"].moveToIndex(0)
				self.refresh()

			elif self.inEpisode is True:
				if self.isVisible == False:
					self.visibility()
					return
		
				finishStillPicture()
		
				selection = self["listview"].getCurrent()
				if selection is not None:
					self.session.openWithCallback(self.leaveMoviePlayer, MoviePlayer, eServiceReference("4097:0:1:0:0:0:0:0:0:0:" + self.episodesdb[selection[1]]["Path"] + ":" + selection[0]))


	def leaveMoviePlayer(self): 
		self.session.nav.playService(None) 
		showStillpicture("/hdd/valerie/media/" + self.selectedSeries + "_backdrop.m1v")

	def KeyExit(self):
		if self.inSeries is True:
			if self.isVisible == False:
				self.visibility()
				return
		
			finishStillPicture()

			self.close()
		elif self.inEpisode is True or self.inSeasons is True:
			self.inSeries = True
			self.inSeasons = False
			self.inEpisode = False
			self["listview"].setList(self.serieslist)
			self["listview"].moveToIndex(self.rememeberSeriesIndex)
			self.refresh()

#------------------------------------------------------------------------------------------


