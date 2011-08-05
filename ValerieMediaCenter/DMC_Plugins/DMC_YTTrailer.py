# -*- coding: utf-8 -*-

# Wrapper for the YYTrailer Plugin by Dr Best
# Allows to start the plugin directly from the librarys

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

gAvailable = False
try:
	from Plugins.Extensions.YTTrailer.plugin import YTTrailer
	gAvailable = True
except Exception, ex:
	printl("DMC_YTTrailer::isAvailable Is not available", None, "E")
	printl("DMC_YTTrailer::isAvailable Exception: " + str(ex), None, "E")
	gAvailable = False

def start(session, args):
	if args.has_key("Title"):
		ytTrailer = YTTrailer(session)
		ytTrailer.showTrailer(args["Title"])
	
if gAvailable is True:
	registerPlugin(Plugin(name=_("View Trailer (YTTrailer by Dr. Best)"), fnc=start, where=Plugin.MENU_MOVIES_PLUGINS))