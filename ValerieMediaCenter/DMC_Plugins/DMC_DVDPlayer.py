# -*- coding: utf-8 -*-

from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
try:
	from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer
	gAvailable = True
except:
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