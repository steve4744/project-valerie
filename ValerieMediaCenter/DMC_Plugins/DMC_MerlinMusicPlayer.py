# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

gAvailable = False
if config.plugins.pvmc.merlinmusicplayer.value is True:
	try:
		from Plugins.Extensions.MerlinMusicPlayer.plugin import MerlinMusicPlayerFileList
		gAvailable = True
	except Exception, ex:
		printl("Merlin Music Player not found => disabling ...", "I")
		config.plugins.pvmc.merlinmusicplayer.value = False
		gAvailable = False

class PVMC_MerlinMusicPlayer(MerlinMusicPlayerFileList):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		MerlinMusicPlayerFileList.__init__(self, session, None)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "MerlinMusicPlayerFileList"

if gAvailable is True:
	p = []
	p.append(Plugin(name=_("MerlinMusicPlayer"), start=PVMC_MerlinMusicPlayer, where=Plugin.MENU_MUSIC))
	registerPlugin(p)