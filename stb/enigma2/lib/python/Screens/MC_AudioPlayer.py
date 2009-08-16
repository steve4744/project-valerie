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

from GlobalFunctions import MC_FolderOptions, MC_FavoriteFolders, MC_FavoriteFolderAdd, MC_FavoriteFolderEdit, MC_AudioInfoView

import os
from os import path as os_path

config.plugins.mc_ap = ConfigSubsection()
config.plugins.mc_ap.showMvi = ConfigYesNo(default=True)
config.plugins.mc_ap.mvi_delay = ConfigInteger(default=10, limits=(5, 999))
config.plugins.mc_ap.showPreview = ConfigYesNo(default=False)
config.plugins.mc_ap.preview_delay = ConfigInteger(default=5, limits=(1, 30))
config.plugins.mc_ap.lastDir = ConfigText(default=resolveFilename(SCOPE_MEDIA))

def getAspect():
	val = AVSwitch().getAspectRatioSetting()
	return val/2

#------------------------------------------------------------------------------------------

class MC_AudioPlayer(Screen, HelpableScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		
		self.mviList = []
		self.mviIndex = 0
		self.mviLastIndex = -1
		
		self.isVisible = True
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		#self.session.nav.stopService()

		# Show Background MVI
		#os.system("/usr/bin/showiframe /usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/background.mvi &")
		
		self.coverArtFileName = ""
		
		self["PositionGauge"] = ServicePositionGauge(self.session.nav)
		
		self["key_red"] = Button("Favorites")
		self["key_green"] = Button("Play All")
		self["key_yellow"] = Button("Playlists")
		self["key_blue"] = Button(_("Settings"))
		
		self["fileinfo"] = Label()
		self["coverArt"] = MediaPixmap()
		
		self["currentfolder"] = Label()
		self["currentfavname"] = Label()
		self.curfavfolder = -1

		self["play"] = Pixmap()
		self["stop"] = Pixmap()

		self["curplayingtitle"] = Label()
		self.currPlaying = 0
		self.PlaySingle = 0

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evEOF: self.doEOF,
				iPlayableService.evStopped: self.StopPlayback,
				iPlayableService.evUser+11: self.__evDecodeError,
				iPlayableService.evUser+12: self.__evPluginError,
				iPlayableService.evUser+13: self["coverArt"].embeddedCoverArt
			})
			
		self["actions"] = HelpableActionMap(self, "MC_AudioPlayerActions", 
			{
				"ok": (self.KeyPlaySingle, "Play selected file"),
				"cancel": (self.Exit, "Exit Audio Player"),
				"left": (self.leftUp, "List Top"),
				"right": (self.rightDown, "List Bottom"),
				"up": (self.up, "List up"),
				"down": (self.down, "List down"),
				"menu": (self.KeyMenu, "File / Folder Options"),
				"video": (self.visibility, "Show / Hide Player"),
				"info": (self.showFileInfo, "Show File Info"),
				"nextBouquet": (self.NextFavFolder, "Next Favorite Folder"),
				"prevBouquet": (self.PrevFavFolder, "Previous Favorite Folder"),
				"stop": (self.StopPlayback, "Stop Playback"),
				"red": (self.FavoriteFolders, "Favorite Folders"),
				"green": (self.KeyPlayAll, "Play All"),
				"yellow": (self.Playlists, "Playlists"),
				"blue": (self.Settings, "Settings"),
			}, -2)
			
		self.aspect = getAspect()
		currDir = config.plugins.mc_ap.lastDir.value
		if not pathExists(currDir):
			currDir = "/"

		self["currentfolder"].setText(str(currDir))
		
		self.filelist = FileList(currDir, useServiceRef = True, showDirectories = True, showFiles = True, matchingPattern = "(?i)^.*\.(mp3|ogg|wav|wave|flac|m4a)")
		self["filelist"] = self.filelist
		self["thumbnail"] = Pixmap()
		
		self.ThumbTimer = eTimer()
		self.ThumbTimer.callback.append(self.showThumb)
		
		self.MviTimer = eTimer()
		self.MviTimer.callback.append(self.showBackgroundMVI)

		self.BlinkingPlayIconTimer = eTimer()
		self.BlinkingPlayIconTimer.callback.append(self.BlinkingPlayIcon)
		self.blinking=False

		self.getMVI()
		#self.showBackgroundMVI()

		self.FileInfoTimer = eTimer()
		self.FileInfoTimer.callback.append(self.updateFileInfo)

	def up(self):
		self["filelist"].up()
		self.ThumbTimer.start(config.plugins.mc_ap.preview_delay.getValue() * 1000, True)

	def down(self):
		self["filelist"].down()
		self.ThumbTimer.start(config.plugins.mc_ap.preview_delay.getValue() * 1000, True)
		
	def leftUp(self):
		self["filelist"].pageUp()
		self.ThumbTimer.start(config.plugins.mc_ap.preview_delay.getValue() * 1000, True)
		
	def rightDown(self):
		self["filelist"].pageDown()
		self.ThumbTimer.start(config.plugins.mc_ap.preview_delay.getValue() * 1000, True)

	def NextFavFolder(self):
		if self.curfavfolder + 1 < config.plugins.mc_favorites.foldercount.value:
			self.curfavfolder += 1
			self.favname = config.plugins.mc_favorites.folders[self.curfavfolder].name.value
			self.folder = config.plugins.mc_favorites.folders[self.curfavfolder].basedir.value
			self["currentfolder"].setText(("%s") % (self.folder))
			self["currentfavname"].setText(("%s") % (self.favname))
			if os.path.exists(self.folder) == True:
				self["filelist"].changeDir(self.folder)
		else:
			return
			
	def PrevFavFolder(self):
		if self.curfavfolder <= 0:
			return
		else:
			self.curfavfolder -= 1
			self.favname = config.plugins.mc_favorites.folders[self.curfavfolder].name.value
			self.folder = config.plugins.mc_favorites.folders[self.curfavfolder].basedir.value
			self["currentfolder"].setText(("%s") % (self.folder))
			self["currentfavname"].setText(("%s") % (self.favname))
			if os.path.exists(self.folder) == True:
				self["filelist"].changeDir(self.folder)

	def KeyPlaySingle(self):
		self.ThumbTimer.stop()
		if self["filelist"].canDescent():
			self["currentfavname"].setText("")
			self.curfavfolder = -1
			self.filelist.descent()
			self["currentfolder"].setText(str(self.filelist.getCurrentDirectory()))
		else:
			self.PlaySingle = 1
			self.PlayService()
			self.BlinkingPlayIconTimer.stop()

	def KeyPlayAll(self):
		self.ThumbTimer.stop()
		if not self["filelist"].canDescent():
			self.PlaySingle = 0
			self.PlayService()
			self.BlinkingPlayIconTimer.start(1000, True)

	def PlayService(self):
		#if self.isVisible == False:
		#	self.visibility()
		#	return

		self.currPlaying = 1
		self.MviTimer.stop()
		
		self.session.nav.playService(self["filelist"].getServiceRef())
		self.FileInfoTimer.start(2000, True)
			
		self["play"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/play_enabled.png")
		self["stop"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/stop_disabled.png")

		path = self["filelist"].getCurrentDirectory() + self["filelist"].getFilename()
		self["coverArt"].updateCoverArt(path)
				
		if config.plugins.mc_ap.showMvi.getValue():
			#self.getMVI()
			self.showBackgroundMVI()

	def JumpToFolder(self, jumpto = None):
		if jumpto is None:
			return
		else:
			self["filelist"].changeDir(jumpto)
			self["currentfolder"].setText(("%s") % (jumpto))
	
	def FavoriteFolders(self):
		self.session.openWithCallback(self.JumpToFolder, MC_FavoriteFolders)

	def StartThumb(self):
		self.session.openWithCallback(self.returnVal, ThumbView, self.filelist.getFileList(), self.filelist.getFilename(), self.filelist.getCurrentDirectory())

	def showThumb(self):
		if config.plugins.mc_ap.showPreview.getValue() == False:
			return
			
		if self["filelist"].canDescent():
			return
		else:
			if self["filelist"].getServiceRef() is not None:
				self.session.nav.stopService()
				self.session.nav.playService(self["filelist"].getServiceRef())
				
				self.currPlaying = 1

				self["play"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/play_enabled.png")
				self["stop"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/stop_disabled.png")

				#self.getMVI()
				self.showBackgroundMVI()
		
				self.FileInfoTimer.start(2000, True)
						
	def returnVal(self, val=0):
		if val > 0:
			for x in self.filelist.getFileList():
				if x[0][1] == True:
					val += 1
			self.filelist.moveToIndex(val)

	def StartExif(self):
		if not self.filelist.canDescent():
			self.session.open(ExifView, self.filelist.getCurrentDirectory() + self.filelist.getFilename(), self.filelist.getFilename())

	def visibility(self, force=1):
		if self.isVisible == True:
			self.isVisible = False
			self.hide()
		else:
			self.isVisible = True
			self.show()
			#self["list"].refresh()

	def BlinkingPlayIcon(self):
		if self.blinking:
			self.blinking=False
			self["play"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/play_disabled.png")
			self.BlinkingPlayIconTimer.start(1000, True)
		else:
			self.blinking=True
			self["play"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/play_enabled.png")
			self.BlinkingPlayIconTimer.start(1000, True)
			
	def StopPlayback(self):
		self.ThumbTimer.stop()

		if self.isVisible == False:
			self.show()
			self.isVisible = True
		
		if self.session.nav.getCurrentService() is None:
			return
		
		#if self.session.nav.getCurrentlyPlayingServiceReference() != self.oldService:
		else:
			self.session.nav.stopService()
			#self.session.nav.playService(self.oldService)
			
			#self.getMVI()
			self.showBackgroundMVI()
				
			self["play"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/play_disabled.png")
			self["stop"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/stop_enabled.png")

			self.currPlaying = 0
			self.BlinkingPlayIconTimer.stop()

	def getMVI(self):
		path = "/usr/saver/"
		for root, dirs, files in os.walk(path):
			for name in files:
				if name.endswith(".mvi"):
					self.mviList.append(name)
		print self.mviList

	def showBackgroundMVI(self):
		if len(self.mviList) > 0:
			order = "/usr/bin/showiframe /usr/saver/" + self.mviList[self.mviIndex] + " &"
			
			if self.mviIndex < len(self.mviList) -1:
				self.mviIndex += 1
			else:
				self.mviIndex = 0
			
			print "MediaCenter: Last MVI Index: " + str(self.mviLastIndex)
			if self.mviLastIndex != self.mviIndex or self.mviLastIndex == -1:
				print order
				os.system(order)
				self.mviLastIndex = self.mviIndex
				time = config.plugins.mc_ap.mvi_delay.getValue() * 1000
				self.MviTimer.start(time, True)
		else:
			print "MediaCenter: No Background MVI Files found ..."
				
	def showFileInfo(self):
		if self["filelist"].canDescent():
			return
		else:
			self.session.open(MC_AudioInfoView, self["filelist"].getCurrentDirectory() + self["filelist"].getFilename() , self["filelist"].getFilename(), self["filelist"].getServiceRef())
	
	def updateFileInfo(self):
		if self["filelist"].canDescent():
			return

		currPlay = self.session.nav.getCurrentService()
		if currPlay is not None:
			stitle = currPlay.info().getInfoString(iServiceInformation.sTagTitle)
			sArtist = currPlay.info().getInfoString(iServiceInformation.sTagArtist)
			sAlbum = currPlay.info().getInfoString(iServiceInformation.sTagAlbum)
			sGenre = currPlay.info().getInfoString(iServiceInformation.sTagGenre)
			sComment = currPlay.info().getInfoString(iServiceInformation.sTagComment)
				
			if stitle == "":
				stitle = currPlay.info().getName().split('/')[-1]
					
			self["fileinfo"].setText("Title: " + stitle + "\nArtist: " +  sArtist + "\nAlbum: " + sAlbum + "\nGenre: " + sGenre + "\nComment: " + sComment)
			self["curplayingtitle"].setText(stitle)
				
	def doEOF(self):
		print "MediaCenter: EOF Event ..."

		if self.PlaySingle == 0:
			print "Play Next File ..."
			self.down()
			self.PlayService()
			self.ThumbTimer.stop()
		else:
			print "Stop Playback ..."
			#self["play"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/play_disabled.png")
			#self["stop"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/icons/stop_enabled.png")
			#self.currPlaying = 0
			#self.ThumbTimer.stop()
			#self.BlinkingPlayIconTimer.stop()
			self.StopPlayback()

	def __evDecodeError(self):
		currPlay = self.session.nav.getCurrentService()
		sVideoType = currPlay.info().getInfoString(iServiceInformation.sVideoType)
		print "[__evDecodeError] video-codec %s can't be decoded by hardware" % (sVideoType)
		self.session.open(MessageBox, _("This Dreambox can't decode %s video streams!") % sVideoType, type = MessageBox.TYPE_INFO,timeout = 20 )

	def __evPluginError(self):
		currPlay = self.session.nav.getCurrentService()
		message = currPlay.info().getInfoString(iServiceInformation.sUser+12)
		print "[__evPluginError]" , message
		self.session.open(MessageBox, message, type = MessageBox.TYPE_INFO,timeout = 20 )


	def Playlists(self):
		self.ThumbTimer.stop()
		self.session.open(MessageBox,"Coming soon ... :)",  MessageBox.TYPE_INFO)

	def KeyMenu(self):
		self.ThumbTimer.stop()
		if self["filelist"].canDescent():
			if self.filelist.getCurrent()[0][1]:
				self.currentDirectory = self.filelist.getCurrent()[0][0]
				self.foldername = self.currentDirectory.split('/')
				self.foldername = self.foldername[-2]
				self.session.open(MC_FolderOptions, self.currentDirectory, self.foldername)
	
	def Settings(self):
		self.ThumbTimer.stop()
		self.session.open(AudioPlayerSettings)

	def Exit(self):
		if self.isVisible == False:
			self.visibility()
			return
			
		if self.filelist.getCurrentDirectory() is None:
			config.plugins.mc_ap.lastDir.value = "/"
		else:
			config.plugins.mc_ap.lastDir.value = self.filelist.getCurrentDirectory()

		self.ThumbTimer.stop()
		self.FileInfoTimer.stop()
		
		del self["coverArt"].picload
		
		config.plugins.mc_ap.save()
		self.session.nav.stopService()
		self.close()


#------------------------------------------------------------------------------------------

class MediaPixmap(Pixmap):
	def __init__(self):
		Pixmap.__init__(self)
		self.coverArtFileName = ""
		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.paintCoverArtPixmapCB)
		self.coverFileNames = ["folder.png", "folder.jpg"]

	def applySkin(self, desktop, screen):
		from Tools.LoadPixmap import LoadPixmap
		noCoverFile = None
		if self.skinAttributes is not None:
			for (attrib, value) in self.skinAttributes:
				if attrib == "pixmap":
					noCoverFile = value
					break
		if noCoverFile is None:
			noCoverFile = resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/no_coverArt.png")
		self.noCoverPixmap = LoadPixmap(noCoverFile)
		return Pixmap.applySkin(self, desktop, screen)

	def onShow(self):
		Pixmap.onShow(self)
		sc = AVSwitch().getFramebufferScale()
		#0=Width 1=Height 2=Aspect 3=use_cache 4=resize_type 5=Background(#AARRGGBB)
		self.picload.setPara((self.instance.size().width(), self.instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))

	def paintCoverArtPixmapCB(self, picInfo=None):
		ptr = self.picload.getData()
		if ptr != None:
			self.instance.setPixmap(ptr.__deref__())

	def updateCoverArt(self, path):
		while not path.endswith("/"):
			path = path[:-1]
		new_coverArtFileName = None
		for filename in self.coverFileNames:
			if fileExists(path + filename):
				new_coverArtFileName = path + filename
		if self.coverArtFileName != new_coverArtFileName:
			self.coverArtFileName = new_coverArtFileName
			if new_coverArtFileName:
				self.picload.startDecode(self.coverArtFileName)
			else:
				self.showDefaultCover()

	def showDefaultCover(self):
		self.instance.setPixmap(self.noCoverPixmap)

	def embeddedCoverArt(self):
		print "[embeddedCoverArt] found"
		self.coverArtFileName = "/tmp/.id3coverart"
		self.picload.startDecode(self.coverArtFileName)



#------------------------------------------------------------------------------------------

class AudioPlayerSettings(Screen):
	skin = """
		<screen position="160,220" size="400,120" title="Audioplayer Settings" >
			<widget name="configlist" position="10,10" size="380,100" />
		</screen>"""
	
	def __init__(self, session):
		self.skin = AudioPlayerSettings.skin
		Screen.__init__(self, session)

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"ok": self.close,
			"cancel": self.close,
			"left": self.keyLeft,
			"right": self.keyRight,
			"0": self.keyNumber,
			"1": self.keyNumber,
			"2": self.keyNumber,
			"3": self.keyNumber,
			"4": self.keyNumber,
			"5": self.keyNumber,
			"6": self.keyNumber,
			"7": self.keyNumber,
			"8": self.keyNumber,
			"9": self.keyNumber
		}, -1)
		
		self.list = []
		self["configlist"] = ConfigList(self.list)
		self.list.append(getConfigListEntry(_("Screensaver Enable"), config.plugins.mc_ap.showMvi))
		self.list.append(getConfigListEntry(_("Screensaver Interval"), config.plugins.mc_ap.mvi_delay))
		self.list.append(getConfigListEntry(_("Autoplay Enable"), config.plugins.mc_ap.showPreview))
		self.list.append(getConfigListEntry(_("Autoplay Delay"), config.plugins.mc_ap.preview_delay))

	def keyLeft(self):
		self["configlist"].handleKey(KEY_LEFT)

	def keyRight(self):
		self["configlist"].handleKey(KEY_RIGHT)
		
	def keyNumber(self, number):
		self["configlist"].handleKey(KEY_0 + number)
