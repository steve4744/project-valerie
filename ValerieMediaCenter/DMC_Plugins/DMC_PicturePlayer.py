# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
if config.plugins.pvmc.pictureplayer.value is True:
	try:
		from Plugins.Extensions.PicturePlayer.plugin import picshow as PicturePlayer
		from Plugins.Extensions.PicturePlayer.plugin import Pic_Setup as PicturePlayerSetup
		from Plugins.Extensions.PicturePlayer.plugin import Pic_Full_View as PicturePlayerFullView
		from Plugins.Extensions.PicturePlayer.plugin import Pic_Thumb as PicturePlayerThumbView
		gAvailable = True
	except:
		printl("PicturePlayer not found => disabling ...", "I")
		config.plugins.pvmc.pictureplayer.value = False
		gAvailable = False

class PVMC_PicturePlayer(PicturePlayer):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		PicturePlayer.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "PVMC_PicturePlayer"
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("PicturePlayer"))

	def KeyBlue(self):
		self.session.openWithCallback(self.setConf, PVMC_PicturePlayerSetup)

#	def KeyGreen(self):
#		self.session.openWithCallback(self.callbackView, PVMC_PicturePlayerThumbView, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory())

#	def KeyOk(self):
#		if self.filelist.canDescent():
#			self.filelist.descent()
#		else:
#			self.session.openWithCallback(self.callbackView, PVMC_PicturePlayerFullView, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory())

class PVMC_PicturePlayerSetup(PicturePlayerSetup):
	def __init__(self, session):
		PicturePlayerSetup.__init__(self, session)
		self.skinName = "PVMC_PicturePlayerSetup"
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("PicturePlayer Setup"))

#class PVMC_PicturePlayerFullView(PicturePlayerFullView):
#	def __init__(self, session):
#		PicturePlayerFullView.__init__(self, session)
#		self.skinName = "PVMC_PicturePlayerFullView"
#		self.onLayoutFinish.append(self.setCustomTitle)
#
#	def setCustomTitle(self):
#		self.setTitle(_("PicturePlayer FullView"))

#class PVMC_PicturePlayerThumbView(PicturePlayerThumbView):
#	def __init__(self, session):
#		PicturePlayerThumbView.__init__(self, session)
#		self.skinName = "PVMC_PicturePlayerThumbView"
#		self.onLayoutFinish.append(self.setCustomTitle)
#
#	def setCustomTitle(self):
#		self.setTitle(_("PicturePlayer ThumbView"))

if gAvailable is True:
	registerPlugin(Plugin(name=_("PicturePlayer"), start=PVMC_PicturePlayer, where=Plugin.MENU_PICTURES))