# -*- coding: utf-8 -*-

from Components.config import config
from Components.config import ConfigYesNo
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

config.plugins.pvmc.plugins.sync = ConfigSubsection()
config.plugins.pvmc.plugins.sync.fastsynconautostart = ConfigYesNo(default=False)

def settings():
	s = []
	s.append((_("Fast Sync on autostart"), config.plugins.pvmc.plugins.sync.fastsynconautostart, ))
	return s

def autostartPlugin(session):
	from Plugins.Extensions.ProjectValerieSync.plugin import autostart
	autostart(session)

def startPlugin(session):
	from Plugins.Extensions.ProjectValerieSync.plugin import ProjectValerieSync
	session.open(ProjectValerieSync)

registerPlugin(Plugin(name=_("Synchronize"), fnc=settings, where=Plugin.SETTINGS))
registerPlugin(Plugin(name=_("Synchronize"), fnc=startPlugin, where=Plugin.MENU_SYSTEM, supportStillPicture=True))
if config.plugins.pvmc.plugins.sync.fastsynconautostart.value is True:
	registerPlugin(Plugin(name=_("Synchronize"), fnc=autostartPlugin, where=Plugin.AUTOSTART))

