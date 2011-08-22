# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
if config.plugins.pvmc.dvdplayer.value is True:
	try:
		from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer
		gAvailable = True
	except:
		printl("DVD Player not found => disabling ...", "I")
		config.plugins.pvmc.dvdplayer.value = False
		gAvailable = False

class PVMC_DVDPlayer(DVDPlayer):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		DVDPlayer.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "DVDPlayer"

if gAvailable is True:
	registerPlugin(Plugin(name=_("DVDPlayer"), start=PVMC_DVDPlayer, where=Plugin.MENU_VIDEOS))
	
	  