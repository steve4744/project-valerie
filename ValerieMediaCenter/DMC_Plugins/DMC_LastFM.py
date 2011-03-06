# -*- coding: utf-8 -*-

from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
try:
	from Plugins.Extensions.LastFM.plugin import main as StartFunction
	gAvailable = True
except:
	gAvailable = False

if gAvailable is True:
	registerPlugin(Plugin(name=_("LastFM"), fnc=StartFunction, where=Plugin.MENU_MUSIC))