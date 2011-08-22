# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
if config.plugins.pvmc.mediaplayer.value is True:
	try:
		from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
		gAvailable = True
	except:
		printl("MediaPlayer not found => disabling ...", "I")
		config.plugins.pvmc.mediaplayer.value = False
		gAvailable = False

class PVMC_MediaPlayer(MediaPlayer):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		MediaPlayer.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "MediaPlayer"

if gAvailable is True:
	p = []
	p.append(Plugin(name=_("MediaPlayer"), start=PVMC_MediaPlayer, where=Plugin.MENU_VIDEOS))
	p.append(Plugin(name=_("MediaPlayer"), start=PVMC_MediaPlayer, where=Plugin.MENU_MUSIC))
	registerPlugin(p)