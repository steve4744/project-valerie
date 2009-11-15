

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
#from Components.ServiceEventTracker import ServiceEventTracker

from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *

from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
#from Screens.InfoBar import MoviePlayer

from Screens.InfoBarGenerics import InfoBarShowHide, \
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarRdsDecoder, \
	InfoBarEPG, InfoBarSeek, InfoBarInstantRecord, \
	InfoBarAudioSelection, InfoBarExtendedAudioSelection, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, \
	InfoBarAspectSelection, InfoBarSubserviceSelection, InfoBarShowMovies, InfoBarTimeshift,  \
	InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
	InfoBarSummarySupport, InfoBarMoviePlayerSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions, \
	InfoBarSubtitleSupport, InfoBarPiP, InfoBarPlugins, InfoBarSleepTimer, InfoBarServiceErrorPopupSupport, InfoBarJobman

from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Plugins.Plugin import PluginDescriptor

from Screens.ChoiceBox import ChoiceBox

class DMC_MoviePlayer(InfoBarShowHide, \
		InfoBarSeek, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications,
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView,
		InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, Screen, InfoBarTeletextPlugin,
		InfoBarServiceErrorPopupSupport):

	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True
		
	def __init__(self, session, service):
		Screen.__init__(self, session)
		
		self["actions"] = HelpableActionMap(self, "MoviePlayerActions",
			{
				"leavePlayer": (self.leavePlayer, _("leave movie player..."))
			})
			
		self["MediaPlayerActions"] = HelpableActionMap(self, "MediaPlayerActions",
			{
				"previous": (self.previousMarkOrEntry, _("play from previous mark or playlist entry")),
				"next": (self.nextMarkOrEntry, _("play from next mark or playlist entry")),
				"subtitles": (self.subtitleSelection, _("Subtitle selection")), 
			}, -2)
		
		for x in HelpableScreen, InfoBarShowHide, \
				InfoBarSeek, \
				InfoBarAudioSelection, InfoBarNotifications, InfoBarSimpleEventView, \
				InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport,\
				InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, \
				InfoBarTeletextPlugin, InfoBarServiceErrorPopupSupport:
			x.__init__(self)
		
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evEOF: self.doEOF,
				iPlayableService.evStopped: self.doEOF,
			})

		self.session.nav.playService(service)
		self.returning = False

	def nextMarkOrEntry(self):
		if not self.jumpPreviousNextMark(lambda x: x):
			self.is_closing = True
			self.close(1)

	def previousMarkOrEntry(self):
		if not self.jumpPreviousNextMark(lambda x: -x-5*90000, start=True):
			self.is_closing = True
			self.close(-1)
	def subtitleSelection(self): 
		from Screens.Subtitles import Subtitles 
		self.session.open(Subtitles) 
			
	def doEOF(self):
		self.session.nav.stopService()
		self.leavePlayer()

	def leavePlayer(self):
		self.is_closing = True

		if config.usage.on_movie_stop.value == "ask":
			list = []
			list.append((_("Yes"), "quit"))
			list.append((_("No"), "continue"))
			if config.usage.setup_level.index >= 2: # expert+
				list.append((_("No, but restart from begin"), "restart"))
			self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)
		else:
			self.close(0)

	def leavePlayerConfirmed(self, answer):
		answer = answer and answer[1]
		if answer == "quit":
			self.close(0)
		elif answer == "restart":
			self.doSeek(0)

	def doEofInternal(self, playing):
		print "--- eofint movieplayer ---"
		self.is_closing = True
		self.close(1)
