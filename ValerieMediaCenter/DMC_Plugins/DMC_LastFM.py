# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
if config.plugins.pvmc.lastfm.value is True:
	try:
		from Plugins.Extensions.LastFM.plugin import main as StartFunction
		gAvailable = True
	except:
		printl("lastFM not found => disabling ...", "I")
		config.plugins.pvmc.lastfm.value = False
		gAvailable = False

if gAvailable is True:
	registerPlugin(Plugin(name=_("LastFM"), fnc=StartFunction, where=Plugin.MENU_MUSIC))