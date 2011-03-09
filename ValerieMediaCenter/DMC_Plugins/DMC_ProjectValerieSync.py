# -*- coding: utf-8 -*-

from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
try:
	from Plugins.Extensions.ProjectValerieSync.plugin import ProjectValerieSync as PluginProjectValerieSync
	from Plugins.Extensions.ProjectValerieSync.plugin import autostart
	gAvailable = True
except:
	gAvailable = False

class ProjectValerieSync(PluginProjectValerieSync):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		PluginProjectValerieSync.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "ProjectValerieSync"

if gAvailable is True:
	registerPlugin(Plugin(name=_("ProjectValerieSync"), start=ProjectValerieSync, where=Plugin.MENU_SYSTEM, supportStillPicture=True))
	registerPlugin(Plugin(name=_(""), fnc=autostart, where=Plugin.AUTOSTART))