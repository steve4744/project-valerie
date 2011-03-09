# -*- coding: utf-8 -*-

from Components.config import config
from Components.config import ConfigYesNo
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

gAvailable = False
try:
	from Plugins.Extensions.ProjectValerieSync.plugin import ProjectValerieSync as PluginProjectValerieSync
	from Plugins.Extensions.ProjectValerieSync.plugin import autostart
	gAvailable = True
except:
	gAvailable = False

config.plugins.pvmc.plugins.sync = ConfigSubsection()
config.plugins.pvmc.plugins.sync.fastsynconautostart = ConfigYesNo(default=False)

class ProjectValerieSync(PluginProjectValerieSync):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		PluginProjectValerieSync.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "ProjectValerieSync"

def settings():
	s = []
	s.append((_("Fast Sync on autostart"), config.plugins.pvmc.plugins.sync.fastsynconautostart, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(name=_("Syncronize"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(name=_("Syncronize"), start=ProjectValerieSync, where=Plugin.MENU_SYSTEM, supportStillPicture=True))
	if config.plugins.pvmc.plugins.sync.fastsynconautostart.value is True:
		registerPlugin(Plugin(name=_("Syncronize"), fnc=autostart, where=Plugin.AUTOSTART))