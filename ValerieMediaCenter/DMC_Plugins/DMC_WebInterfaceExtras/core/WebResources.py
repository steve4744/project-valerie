# -*- coding: utf-8 -*-
from threading import Thread

from Components.config import config
from Components.config import ConfigInteger
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebData import WebData
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebHelper import WebHelper

from Plugins.Extensions.ProjectValerie.DMC_Global import Update
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
MediaInfo = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

gAvailable = False
try:
	from twisted.web.server import Site
	from twisted.web.static import File
	from twisted.internet   import reactor, threads
	from twisted.web.resource import Resource
	
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
class Home(Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("Home")
		
		currentVersion = config.plugins.pvmc.version.value
				
		finalOutput = finalOutput.replace("<!-- CURRENT_VERSION -->", currentVersion)
		
		updateNeeded = Update().checkForUpdate();
		
		if (updateNeeded == False):
			finalOutput = finalOutput.replace("<!-- LATEST_VERSION -->", " (no Update needed)")
		else:
			finalOutput = finalOutput.replace("<!-- LATEST_VERSION -->", "(found new version " + updateNeeded + ")")
		
		
		return utf8ToLatin(finalOutput)

##
#
##		
class Movies(Resource):
	def render_GET(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerieSync.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
				
		finalOutput = WebData().getHtmlCore("Movies", True)
			
		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Movies/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("movies")
		
		for entry in entries:
			##
			# Todo should be escaped not changed ;-)
			# leads to a javascript error if ' or " is in the string
			##
			if type(entry) == MediaInfo:
				entry.Plot = WebData().cleanStrings(entry.Plot)
				entry.Tag = WebData().cleanStrings(entry.Tag)

			evtEdit = WebData().getEditString(entry, "isMovie")
			evtDelete = WebData().getDeleteString(entry, "isMovie")
			
			tableBody += u"""   <tr>
							<td><img src=\"http://val.duckbox.info/convertImg2/poster/%s_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%d</td>
							<td><a href=http://www.imdb.com/title/%s/ target="_blank">%s</a></td>
							<td>%s</td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>
							</td>
						  </tr>
					""" % (entry.ImdbId, entry.Title, entry.Year, entry.ImdbId, entry.ImdbId, entry.Filename + u"." + entry.Extension, evtEdit, evtDelete)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)

##
#
##
class TvShows(Resource):
	def render_GET(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerieSync.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
	
		finalOutput = WebData().getHtmlCore("TvShows", True)
			
		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/TvShows/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("tvshows")

		for entry in entries:
			##
			# Todo should be escaped not changed ;-)
			# leads to a javascript error if ' or " is in the string
			##
			if type(entry) == MediaInfo:
				entry.Plot = WebData().cleanStrings(entry.Plot)
				entry.Tag = WebData().cleanStrings(entry.Tag)

			evtShowEpisodes = WebData().getEpisodesOfTvShow(entry.TheTvDbId)
			evtEdit = WebData().getEditString(entry, "isTvShow")
			evtDelete = WebData().getDeleteString(entry, "isTvShow")
			
			tableBody += u"""   <tr>
							<td><img src=\"http://val.duckbox.info/convertImg2/poster/%s_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%d</td>
							<td>%s</td>
							<td><a href=http://thetvdb.com/index.php?tab=series&id=%s target="_blank">%s</a></td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/showEpisodes.png" alt="show Episodes" title="show Episodes" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>
							</td>
						    </tr>
			""" % (entry.TheTvDbId, entry.Title, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.TheTvDbId, evtShowEpisodes, evtEdit, evtDelete)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)

##
#
##
class Episodes(Resource):
	def render_GET(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerieSync.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("Episodes", True)
		
		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Episodes/Header.tpl")
		tableBody = u""
		
		TheTvDbId = request.args["TheTvDbId"][0]
		printl("TheTvDbId: " + TheTvDbId, "I")
		
		entries = WebData().getData("episodes", TheTvDbId)
		
		for entry in entries:
			##
			# Todo should be escaped not changed ;-)
			# leads to a javascript error if ' or " is in the string
			##
			if type(entry) == MediaInfo:
				entry.Plot = WebData().cleanStrings(entry.Plot)
				entry.Tag = WebData().cleanStrings(entry.Tag)

			evtEdit = WebData().getEditString(entry, "isEpisode")
			evtDelete = WebData().getDeleteString(entry, "isEpisode")
			
			tableBody += u"""   <tr>
							<td><img src=\"http://val.duckbox.info/convertImg2/poster/%s_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%d</td>
							<td>%d</td>
							<td>%d</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>
							</td>
						    </tr>
			""" % (entry.TheTvDbId, entry.Title, entry.Season, entry.Episode, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.Filename + u"." + entry.Extension, evtEdit, evtDelete)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)
	
##
#
##
class Failed(Resource):
	def render_GET(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerieSync.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
				
		finalOutput = WebData().getHtmlCore("Failed", True)

		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Failed/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("failed")
		
		for entry in entries:
			##
			# Todo should be escaped not changed ;-)
			# leads to a javascript error if ' or " is in the string
			##
			if type(entry) == MediaInfo:
				entry.Plot = WebData().cleanStrings(entry.Plot)
				entry.Tag = WebData().cleanStrings(entry.Tag)

			tableBody += u"""   <tr>
								<td>%s</td>
								<td>%s</td>
								<td>%s</td>
							    </tr>
						""" % (entry.Path + u"/" + entry.Filename + u"." + entry.Extension, entry.CauseStr, entry.Description)
				
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)

##
#
##
class MediaInfo(Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
				
		finalOutput = WebData().getHtmlCore("MediaInfo", True)
	
		return utf8ToLatin(finalOutput)



##
#
##		
class Options (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("Options", True)
	
		return utf8ToLatin(finalOutput)		

##
#
##		
class Logs (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("Logs")
	
		return utf8ToLatin(finalOutput)	

##
#
##		
class Valerie (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("Logs" , False, "Valerie")
	
		return utf8ToLatin(finalOutput)	

##
#
##		
class Enigma (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
				
		finalOutput = WebData().getHtmlCore("Logs" , False, "Enigma")
	
		return utf8ToLatin(finalOutput)		

##
#
##		
class Extras (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("Extras")
	
		return utf8ToLatin(finalOutput)
##
#
##		
class Backup (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
				
		finalOutput = WebData().getHtmlCore("Extras" , True, "Backup")
	
		return utf8ToLatin(finalOutput)	

##
#
##		
class Restore (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("Extras" , True, "Restore")
	
		return utf8ToLatin(finalOutput)
		