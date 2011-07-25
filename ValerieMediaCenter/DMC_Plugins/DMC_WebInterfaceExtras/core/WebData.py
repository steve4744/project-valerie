from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebHelper import WebHelper
from Components.config import config
from urllib import urlencode

import sys
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

##
#
##	
class WebData():
	def getData(self, type, param=None):
		global Manager
		if Manager is None:
			from Plugins.Extensions.ProjectValerieSync.Manager import Manager
		
		dataRows = []
		
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
		elif type == "options.global":
			from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin
			dataRows = []
			plugins = getPlugins(where=Plugin.SETTINGS)
			for plugin in plugins: 
				pluginSettingsList = plugin.fnc() 
				for pluginSetting in pluginSettingsList: 
					if len(plugin.name) > 0:
						text = "[%s] %s" % (plugin.name, pluginSetting[0], )
					else:
						text = "%s" % (pluginSetting[0], )
					dataRows.append((text, pluginSetting[1]))
		elif type == "options.sync":
			from Plugins.Extensions.ProjectValerieSync.PathsConfig import PathsConfig
			dataRows = PathsConfig().getInstance()
		
		return dataRows
	##
	# 
	# 
	##
	def getHtmlCore (self, webResource, functions = False, submenu = None ):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
				
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
				if (webResource == "Movies" or webResource == "TvShows" or webResource == "Episodes" or webResource == "Failed"):
					if (config.plugins.pvmc.plugins.webinterface.usepagination.value == True):
						Pagination = '"bPaginate": true,"sScrollY": 768,'
					else:
						Pagination = '"bPaginate": false,\n"bScrollInfinite": true,'
					customJS = customJS.replace("<!-- PAGINATION_FLAG -->", Pagination)	
			else:
				customJS = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/" + submenu + "/Functions.js")
				if (webResource == "Movies" or webResource == "TvShows" or webResource == "Episodes" or webResource == "Failed"):
					if (config.plugins.pvmc.plugins.webinterface.usepagination.value == True):
						Pagination = '"bPaginate": true,"sScrollY": 768,'
					else:
						Pagination = '"bPaginate": false,\n"bScrollInfinite": true,'
					customJS = customJS.replace("<!-- PAGINATION_FLAG -->", Pagination)	
			
			finalOutput = finalOutput.replace("<!-- CUSTOM_JAVASCRIPT -->", customJS)
		
		return utf8ToLatin(finalOutput)
	
	##
	#
	#
	##
	def getEpisodesOfTvShow (self, TheTvDbId):
		onclick = "javascript:window.open('/episodes?TheTvDbId=" + TheTvDbId + "', '_self');"
		
		return onclick
	
	##
	#
	#
	##
	def getEditString (self, entry, type):
		### <!-- build edit string -->
		onclick  = "javascript:window.open('/mediainfo?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'mode':"edit"}) + "&"		
		onclick  += urlencode({'usePath':"true"}) + "&"
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
		onclick  += urlencode({'Poster':entry.Poster}) + "&"	
		onclick  += urlencode({'Backdrop':entry.Backdrop}) + "&"		
		onclick  += urlencode({'Path':entry.Path}) + "&"
		onclick  += urlencode({'Filename':entry.Filename}) + "&"
		onclick  += urlencode({'Extension':entry.Extension})
		onclick  += "', '_self');"
		
		return onclick
	
	def getDeleteString (self, entry, type):
		### <!-- build delete string -->
		onclick = "javascript:if (confirm('Are you sure to delete the selected record?')) {window.open('/action?method=delete&what="
		onclick  += str(type) + "&"
		
		if (type == 'isMovie'):
			onclick  += "ImdbId=" + str(entry.ImdbId)
		elif (type == 'isTvShow'):
			onclick  += "TheTvDbId=" + str(entry.TheTvDbId)
		elif (type == 'isEpisode'):
			onclick  += "TheTvDbId=" + str(entry.TheTvDbId) + "&Season=" + str(entry.Season) + "&Episode=" + str(entry.Episode)
		onclick  += "', '_self')} else { return};"
		
		return onclick
	
	##
	# DEPRECADED - not used anymore for now
	#
	##
	def getAlternativesString (self, entry, type):
		### <!-- build alternatives string -->
		onclick  = "javascript:window.open('/alternatives?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'modus':"existing"}) + "&"
		onclick  += urlencode({'by':"Title"}) + "&"
		onclick  += urlencode({'oldImdbId':entry.ImdbId}) + "&"
		onclick  += urlencode({'Title':entry.Title}) + "&"
		onclick  += urlencode({'Path':entry.Path}) + "&"
		onclick  += urlencode({'Filename':entry.Filename}) + "&"
		onclick  += urlencode({'Extension':entry.Extension})
		onclick  += "', '_self');"
		
		return onclick

	##
	#
	#
	##
	def getApplyString (self, entry, existing):
		### <!-- build apply string -->
		onclick  = "javascript:window.open('/addrecord?"
		onclick  += urlencode({'type':entry.type}) + "&"
		onclick  += urlencode({'ImdbId':entry.ImdbId}) + "&"
		onclick  += urlencode({'oldImdbId':entry.oldImdbId}) + "&"
		
		if existing == "true":
			onclick  += urlencode({'usePath':"true"}) + "&"
			onclick  += urlencode({'Path':entry.Path}) + "&"
			onclick  += urlencode({'Filename':entry.Filename}) + "&"
			onclick  += urlencode({'Extension':entry.Extension})
		else:
			onclick  += urlencode({'usePath':"false"})
		onclick  += "', '_self');"
		
		return onclick
	
	##
	#
	#
	##
	def getAddEpisodeString	(self, entry, type):
		### <!-- build addEpisode string -->
		onclick  = "javascript:window.open('/addrecord?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'ImdbId':entry.ImdbId}) + "&"
		onclick  += urlencode({'TheTvDbId':entry.TheTvDbId}) + "&"
		onclick  += "', '_self');"
		
		return onclick	