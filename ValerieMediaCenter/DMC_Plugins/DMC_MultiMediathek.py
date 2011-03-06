# -*- coding: utf-8 -*-

from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
try:
	from Plugins.Extensions.MultiMediathek.plugin import MultiMediathek
	gAvailable = True
except:
	gAvailable = False

class PVMC_MultiMediathek(MultiMediathek):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		MultiMediathek.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "MultiMediathek"

if gAvailable is True:
	registerPlugin(Plugin(name=_("MultiMediathek"), start=PVMC_MultiMediathek, where=Plugin.MENU_VIDEOS))