# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
if config.plugins.pvmc.multimediathek.value is True:
	try:
		from Plugins.Extensions.MultiMediathek.plugin import MultiMediathek
		gAvailable = True
	except:
		printl("MultiMediathek not found => disabling ...", "I")
		config.plugins.pvmc.multimediathek.value = False
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