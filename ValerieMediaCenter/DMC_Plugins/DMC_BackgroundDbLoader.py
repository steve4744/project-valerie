# -*- coding: utf-8 -*-

from threading import Thread

from Components.config import config
from Components.config import ConfigYesNo
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

gAvailable = False
gLateImport = False
try:
	from Plugins.Extensions.ProjectValerieSync.Manager import Manager
	
	gAvailable = True
except Exception, ex:
	printl("DMC_BackgroundDbLoader::isAvailable Is not available", None, "E")
	printl("DMC_BackgroundDbLoader::isAvailable Exception: " + str(ex), None, "E")
	gAvailable = False

config.plugins.pvmc.plugins.backgrounddbloader = ConfigSubsection()
config.plugins.pvmc.plugins.backgrounddbloader.autoload = ConfigYesNo(default = True)

class BackgroundDbLoader(Thread):
	def run(self):
		global gLateImport
		if gLateImport:
			from Plugins.Extensions.ProjectValerieSync.Manager import Manager
		m = Manager()

def autostart(session):
	try:
		thread = BackgroundDbLoader()
		thread.start()
	except Exception, ex:
		printl("Exception(Can be ignored): " + str(ex), __name__, "W")

def settings():
	s = []
	s.append((_("Autoload Database on start"), config.plugins.pvmc.plugins.backgrounddbloader.autoload, ))
	return s

if gAvailable is False:
	printl("WORKAROUND: Force displaying of this plugin!", __name__, "W")
	gAvailable = True
	gLateImport = True

if gAvailable is True:
	registerPlugin(Plugin(name=_("BackgroundDbLoader"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(name=_("BackgroundDbLoader"), fnc=autostart, where=Plugin.AUTOSTART))