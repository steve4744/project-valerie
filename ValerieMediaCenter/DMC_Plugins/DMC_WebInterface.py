# -*- coding: utf-8 -*-

from   threading import Thread

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

gAvailable = False
try:
	from twisted.web.server import Site
	from twisted.web.static import File
	from twisted.internet   import reactor, threads
	gAvailable = True
except:
	gAvailable = False



def autostart(session):
	running_defered = []
	root = File('/tmp/valerie/log', defaultType="text/plain")
	site = Site(root)
	reactor.listenTCP(8888, site, interface="0.0.0.0")

if gAvailable is True:
	registerPlugin(Plugin(name=_(""), fnc=autostart, where=Plugin.AUTOSTART))