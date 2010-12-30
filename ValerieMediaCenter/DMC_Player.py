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


class PVMC_Player(MoviePlayer):
	def __init__(self, session, playlist, notifyNextEntry=None):
		self.session = session
		self.playlist = playlist
		
		self.notifyNextEntry = notifyNextEntry
		
		if isinstance(playlist, list):
			self.isPlaylist = True
			self.current = 0
			firstPath = playlist[0][0]
			firstName = playlist[0][1]
			if firstPath.endswith(".ts"):
				type = 1
			else:
				type = 4097
			ref = eServiceReference(type, 0, firstPath)
			ref.setName(firstName)
			MoviePlayer.__init__(self, session, ref)
		else:
			self.isPlaylist = False
			MoviePlayer.__init__(self, session, playlist)
		self.skinName = "MoviePlayer"

	def leavePlayer(self, eof=False):
		list = []
		list.append((_("Yes"), "quit"))

		if self.nextPlaylistEntryAvailable() is True:
			list.append((_("Yes, but play next episode"), "next"))
		if eof is False:
			list.append((_("No, continue"), "continue"))
		
		from Screens.ChoiceBox import ChoiceBox
		self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)

	def leavePlayerConfirmed(self, answer):
		if answer is not None and len(answer) >= 2: # I dont get how ChoiceBox can return None, but well this has happend in Issue 88
			print "ANSWER:", answer[1]
			if answer[1] == "quit":
				self.close()
			elif answer[1] == "next":
				self.nextPlaylistEntry()
				if self.notifyNextEntry is not None:
					self.notifyNextEntry()
			elif answer[1] == "continue":
				return None
		else:
			self.close()

# Some functions need to be overriden so they are not called
	def showMovies(self):
		return None

	def startTeletext(self):
		return None

	def showExtensionSelection(self):
		return None

	def mainMenu(self):
		return None

##
# Is notified if movie has ended
	def doEofInternal(self, playing):
		if self.execing and playing:
			self.leavePlayer(True)

	def playPlaylistEntry(self):
		selectedPath = self.playlist[self.current][0]
		selectedName = self.playlist[self.current][1]
		if selectedPath.endswith(".ts"):
			type = 1
		else:
			type = 4097
		ref = eServiceReference(type, 0, selectedPath)
		ref.setName(selectedName)
		self.session.nav.playService(ref)
		
	def nextPlaylistEntry(self):
		if self.nextPlaylistEntryAvailable():
			self.current += 1
			self.playPlaylistEntry()

	def nextPlaylistEntryAvailable(self):
		if self.isPlaylist and len(self.playlist) > 1:
			if (self.current + 1) < len(self.playlist):
				return True
		return False
		
