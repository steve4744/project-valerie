# -*- coding: utf-8 -*-

import gettext
import os
from   os import environ

from enigma import eTimer, eServiceReference
from Components.Language import language
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBar import MoviePlayer
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, SCOPE_LANGUAGE

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin, registerPlugin

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

class PVMC_Player(MoviePlayer):
	def __init__(self, session, playlist, notifyNextEntry=None):
		self.session = session
		self.playlist = playlist
		
		self.progressTimer = eTimer()
		self.progressTimer.callback.append(self.progressUpdate)
		self.progressTimer.start(1000)
		
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
			self.playing = True
			MoviePlayer.__init__(self, session, ref)
		else:
			self.isPlaylist = False
			self.playing = True
			MoviePlayer.__init__(self, session, playlist)
		self.skinName = "MoviePlayer"

	def leavePlayer(self, eof=False):
		list = []
		
		if self.nextPlaylistEntryAvailable() is True:
			list.append((_("Yes, but play next episode"), "next"))
		
		list.append((_("Yes"), "quit"))
		
		if eof is False:
			list.append((_("No, continue"), "continue"))
		
		self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)

	def leavePlayerConfirmed(self, answer):
		if answer is not None and len(answer) >= 2: # I dont get how ChoiceBox can return None, but well this has happend in Issue 88
			print "ANSWER:", answer[1]
			if answer[1] == "quit":
				self.playing = False
				self.close()
			elif answer[1] == "next":
				self.nextPlaylistEntry()
				if self.notifyNextEntry is not None:
					self.notifyNextEntry()
			elif answer[1] == "continue":
				return None

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
		self.playing = False
		if self.execing and playing:
			self.leavePlayer(True)

	progressUpdateCounter = 0
	progressUpdateCounterMargin = 10*60 #10min
	progressUpdateNextPercentMargin = 0
	progressUpdateNextPercentDistance = 5

	def progressUpdate(self):
		self.progressUpdateCounter += 1
		service = self.session.nav.getCurrentService()
		seek = service and service.seek()
		if seek != None:
			rLen = seek.getLength()
			rPos = seek.getPlayPosition()
			if not rLen[0] and not rPos[0]:
				pos = int(rPos[1] / 90000)
				len = int(rLen[1] / 90000)
				if len > 0: #DM seems to return zero sometimes ?
					percent = int((pos * 100.0) / len)
				elif self.progressUpdateNextPercentMargin > 0:
					percent = self.progressUpdateNextPercentMargin - self.progressUpdateNextPercentDistance
				else:
					percent = 0
				printl("percent: " + str(percent) + " len: " + str(len) + " pos: " + str(pos), self)
				printl("self.progressUpdateCounter: " + str(self.progressUpdateCounter), self)
				printl("self.progressUpdateNextPercentMargin: " + str(self.progressUpdateNextPercentMargin), self)
				if self.progressUpdateCounter >= self.progressUpdateCounterMargin:
					self.progressUpdateCounter = 0
					self. communicatelApiProgressAndDuration(percent, len)
				elif percent >= self.progressUpdateNextPercentMargin:
					self.progressUpdateCounter = 0
					self.progressUpdateNextPercentMargin += self.progressUpdateNextPercentDistance
					self. communicatelApiProgressAndDuration(percent, len)

	def communicatelApiProgressAndDuration(self, progress, duration):
		args = {}
		args["progress"] = progress
		args["duration"] = duration
		plugins = getPlugins(where=Plugin.INFO_PLAYBACK)
		for plugin in plugins:
			pluginSettingsList = plugin.fnc(args)

	def playPlaylistEntry(self):
		selectedPath = self.playlist[self.current][0]
		selectedName = self.playlist[self.current][1]
		if selectedPath.endswith(".ts"):
			type = 1
		else:
			type = 4097
		ref = eServiceReference(type, 0, selectedPath)
		ref.setName(selectedName)
		self.playing = True
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
