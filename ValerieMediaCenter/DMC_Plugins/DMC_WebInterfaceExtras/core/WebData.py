# -*- coding: utf-8 -*-
from threading import Thread

from Components.config import config
from Components.config import ConfigInteger
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebHelper import WebHelper

import sys
from urllib import urlencode

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
class WebData():
	def getData(self, type, param=None):
		
		manager = Manager()
		
		if type == "movies":
			dataRows = manager.getAll(Manager.MOVIES)
		elif type == "tvshows":
			dataRows = manager.getAll(Manager.TVSHOWS)
		elif type == "episodes":
			if param != None:
				dataRows = manager.getAll(Manager.TVSHOWSEPISODES, param)
			else:
				dataRows = manager.getAll(Manager.TVSHOWSEPISODES)
		elif type == "failed":
			dataRows = manager.getAll(Manager.FAILED_ALL)
		
		return dataRows
	##
	# param submenu
	# values = None 
	##
	def getHtmlCore (self, webResource, functions = False, submenu = None ):
				
		htmlCore = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/index.html")
		
		mainMenu = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/global/tpl/mainMenu.tpl")
		customSubMenu = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/SubMenu.tpl")
		
		if (submenu == None):
			customContent = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/Content.tpl")
		else:
			customContent = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/" + submenu + "/Content.tpl")

		
		finalOutput 	= htmlCore.replace("<!-- GLOBAL_MAINMENU -->", mainMenu)
		finalOutput 	= finalOutput.replace("<!-- CUSTOM_CONTENT -->", customContent)
		finalOutput 	= finalOutput.replace("<!-- CUSTOM_SUBMENU -->", customSubMenu)
		
		if (functions == True):
			if (submenu == None):
				customJS = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/Functions.js")
			else:
				customJS = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/" + submenu + "/Functions.js")
			
			finalOutput = finalOutput.replace("<!-- CUSTOM_JAVASCRIPT -->", customJS)
		
		return utf8ToLatin(finalOutput)
	
	def cleanStrings(self, string):
		string = string.replace("'","")
		string = string.replace('"','')
		string = string.replace('?','')
		
		return string
		
	def getEpisodesOfTvShow (self, tvdbid):
		onclick = "javascript:window.open('/episodes?tvdbid=" + tvdbid + "');"
		
		return onclick
	
	def getEditString (self, entry, type):
		### <!-- build edit string -->
		onclick  = "javascript:$('#sm_save').show();window.open('/mediainfo?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'ImdbId':entry.ImdbId}) + "&"
		onclick  += urlencode({'TheTvDbId':entry.TheTvDbId}) + "&"
		onclick  += urlencode({'Title':entry.Title}) + "&"
		onclick  += urlencode({'Season':entry.Season}) + "&"
		onclick  += urlencode({'Episode':entry.Episode}) + "&"
		onclick  += urlencode({'Plot':entry.Plot}) + "&"
		onclick  += urlencode({'Runtime':entry.Runtime}) + "&"
		onclick  += urlencode({'Year':entry.Year}) + "&"
		onclick  += urlencode({'Genres':entry.Genres}) + "&"
		onclick  += urlencode({'Tag':entry.Tag}) + "&"
		onclick  += urlencode({'Popularity':entry.Popularity}) + "&"
		onclick  += urlencode({'Path':entry.Path}) + "&"
		onclick  += urlencode({'Filename':entry.Filename}) + "&"
		onclick  += urlencode({'Extension':entry.Extension})
		onclick  += "');"
		
		return onclick
	
	def getDeleteString (self, entry, type):
		### <!-- build delete string -->
		onclick = "javascript:$('#sm_save').show();window.open('/action?method=delete&what="
		onclick  += str(type) + "&"
		
		if (type == 'isMovie'):
			onclick  += "imdbid=" + str(entry.ImdbId) + "&"
		elif (type == 'isTvShow'):
			onclick  += "thetvdbid=" + str(entry.TheTvDbId) + "&"
		elif (type == 'isEpisode'):
			onclick  += "thetvdbid=" +str(entry.TheTvDbId) + "&"
		onclick  += "');"
		
		return onclick
