# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
if config.plugins.pvmc.dreamnetcast.value is True:
	try:
		try:
			from Plugins.Bp.geminidreamnetcast.plugin import dreamnetstart
		except:
			from Plugins.Bp.geminidreamnetcast.geminidreamnetcast.plugin import dreamnetstart
		gAvailable = True
	except Exception, ex:
		printl("Dreamnetcast not found => disabling ...", "I")
		config.plugins.pvmc.dreamnetcast.value = False
		gAvailable = False

if gAvailable is True:
	registerPlugin(Plugin(name=_("Dreamnetcast"), fnc=dreamnetstart, where=Plugin.MENU_MUSIC))