# -*- coding: utf-8 -*-

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
try:
	try:
		from Plugins.Bp.geminidreamnetcast.geminidreamnetcast import geminidreamnetcast
	except:
		from Plugins.Bp.geminidreamnetcast import geminidreamnetcast
	gAvailable = True
except Exception, ex:
	printl("Exception(" + str(type(ex)) + "): " + str(ex), __name__, "E")
	gAvailable = False

if gAvailable is True:
	registerPlugin(Plugin(name=_("Dreamnetcast"), start=geminidreamnetcast, where=Plugin.MENU_MUSIC))