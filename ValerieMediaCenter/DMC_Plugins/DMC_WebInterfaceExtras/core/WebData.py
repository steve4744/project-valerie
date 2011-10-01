##############################################################################
# THIS FILES PROVIDES ...
##############################################################################

from urllib import urlencode
from Components.config import config

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

import sys
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

##########################
# THIS CLASS GETS THE DATA FROM VALERIE PYTHON PART
# PARAMS:	type 	"movies" | "tvshows" | "episodes" | "EpisodesOfSerie" | "failed" |
#					"MediaInfo_isMovie" | "MediaInfo_isTvShow" | "MediaInfo_isEpisode" |
#					"options.global" | "options.sync"
#			param 	"TODO WHAT ARE POSSIBLE PARAMS" DEFAULT = NONE
##########################
class WebData():
	def getData(self, type, param=None):
		global Manager
		if Manager is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		
		dataRows = []
		
		manager = Manager()
		printl("TYPE: " + type)
		if type == "movies":
			dataRows = manager.getMoviesValues()
		elif type == "tvshows":
			dataRows = manager.getSeriesValues()
		elif type == "episodes":
			if param != None:
				dataRows = manager.getEpisodesWithTheTvDbId(param)				
			else:
				dataRows = manager.getEpisodes()				
		elif type == "EpisodesOfSerie":
			dataRows = manager.getEpisodes(param)	
		elif type == "failed":
			dataRows = manager.getFailed()

		elif type == "MediaInfo_isMovie":
			dataRows = manager.getMovie(param)
		elif type == "MediaInfo_isTvShow":
			dataRows = manager.getSerie(param)
		elif type == "MediaInfo_isEpisode":
			dataRows = manager.getEpisode(param)
		elif type == "MediaInfo_isFailed":
			dataRows = manager.getFailedItem(param)
			
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
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PathsConfig import PathsConfig
			dataRows = PathsConfig().getInstance()
		
		return dataRows
