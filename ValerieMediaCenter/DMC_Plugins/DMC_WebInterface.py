# -*- coding: utf-8 -*-
from threading import Thread

from Components.config import config
from Components.config import ConfigInteger
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

from DMC_WebInterfaceExtras.core import WebActions
from DMC_WebInterfaceExtras.core import WebResources

#------------------------------------------------------------------------------------------

gAvailable = False
try:
	from twisted.web.server import Site
	from twisted.web.static import File
	from twisted.internet   import reactor, threads
	from twisted.web.resource import Resource
	try:
		from Plugins.Extensions.ProjectValerieSync.Manager import Manager
		from Plugins.Extensions.ProjectValerieSync.MediaInfo import *
		from Plugins.Extensions.ProjectValerieSync.Utf8 import *
	except:
		from ..ProjectValerieSync.Manager import Manager
		from ..ProjectValerieSync.MediaInfo import *
		from ..ProjectValerieSync.Utf8 import *
	
	gAvailable = True
except Exception, ex:
	printl("DMC_WebInterfaceExtras::isAvailable Is not available", None, "E")
	printl("DMC_WebInterfaceExtras::isAvailable Exception: " + str(ex), None, "E")
	gAvailable = False

config.plugins.pvmc.plugins.webinterface = ConfigSubsection()
config.plugins.pvmc.plugins.webinterface.port = ConfigInteger(default = 8888, limits=(1, 65535) )

##
#
##
def autostart(session):
	try:
		root = Resource()
		
		#Dynamic Pages
		root.putChild("", WebResources.Home())
		root.putChild("movies", WebResources.Movies())
		root.putChild("tvshows", WebResources.TvShows())
		root.putChild("failed", WebResources.Failed())
		root.putChild("extras", WebResources.Extras())
		root.putChild("options", WebResources.Options())
		root.putChild("logs", WebResources.Logs())
		root.putChild("valerie", WebResources.Valerie())
		root.putChild("enigma", WebResources.Enigma())
		
		#Static Pages, CSS, JS
		root.putChild("content", File(utf8ToLatin(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterfaceExtras/content"), defaultType="text/plain"))
		
		#Folder Lists
		root.putChild("vlog", File(config.plugins.pvmc.tmpfolderpath.value + 'log', defaultType="text/plain"))
		root.putChild("elog", File('/hdd/', defaultType="text/plain"))
		#root.putChild("valerie", File(config.plugins.pvmc.tmpfolderpath.value, defaultType="text/plain"))
		
		#Action pages without MainMenu-Entry
		root.putChild("action", WebActions.WebActions())
		root.putChild("mediainfo", WebResources.MediaInfo())
		root.putChild("episodes", WebResources.Episodes())
		
		#Action pages in SubMenu
		root.putChild("backup", WebResources.Backup())
		root.putChild("restore", WebResources.Restore())
		
		
		site = Site(root)
		port = config.plugins.pvmc.plugins.webinterface.port.value
		reactor.listenTCP(port, site, interface="0.0.0.0")
	except Exception, ex:
		printl("Exception(Can be ignored): " + str(ex), __name__, "W")

def settings():
	s = []
	s.append((_("Port"), config.plugins.pvmc.plugins.webinterface.port, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(name=_("WebInterface"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(name=_("WebInterface"), fnc=autostart, where=Plugin.AUTOSTART_E2))
