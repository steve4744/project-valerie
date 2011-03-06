# -*- coding: utf-8 -*-

from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
try:
	from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
	gAvailable = True
except:
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