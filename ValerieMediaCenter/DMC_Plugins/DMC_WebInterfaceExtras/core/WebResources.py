from Components.config import config
from Components.config import ConfigSelection

from twisted.web.resource import Resource

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.DMC_Global import Update
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebData import WebData
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebHelper import WebHelper
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
MediaInfo = None
utf8ToLatin = None
MediaInfo = None
MobileImdbComProvider = None
# --- LAZY IMPORTS ---

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
			evtEdit = WebData().getEditString(entry, "isMovie")
			evtAlternatives = WebData().getAlternativesString(entry, "isMovie")
			evtDelete = WebData().getDeleteString(entry, "isMovie")
			
			tableBody += u"""   <tr>
							<td><img src=\"http://val.duckbox.info/convertImg2/poster/%s_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%d</td>
							<td><a href=http://www.imdb.com/title/%s/ target="_blank">%s</a></td>
							<td>%s</td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/showAlternatives.png" alt="alternatives" title="alternatives" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>
							</td>
						  </tr>
					""" % (entry.ImdbId, entry.Title, entry.Year, entry.ImdbId, entry.ImdbId, entry.Filename + u"." + entry.Extension, evtEdit, evtAlternatives, evtDelete)
		
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
class Alternatives(Resource):
	def render_GET(self, request):
		global utf8ToLatin
		global MediaInfo
		global MobileImdbComProvider
		
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerieSync.MediaInfo import MediaInfo
		if MobileImdbComProvider is None:
			from Plugins.Extensions.ProjectValerieSync.MobileImdbComProvider import MobileImdbComProvider
				
		finalOutput = WebData().getHtmlCore("Alternatives", True)
		
		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Alternatives/Header.tpl")
		tableBody = u""
		
		mediainfo = MediaInfo()
		mediainfo.ImdbId = "";
		mediainfo.SearchString = "";

		mediainfo.SearchString = request.args["Title"][0]
		entries = MobileImdbComProvider().getAlternatives(mediainfo)
		
		for entry in entries:
			existing = "false"
			entry.type = request.args["type"][0]
			
			if request.args["modus"][0] == "existing":
				entry.Path = request.args["Path"][0]
				entry.Filename = request.args["Filename"][0]
				entry.Extension = request.args["Extension"][0]
				existing = "true"
		
			evtApply = WebData().getApplyString(entry, existing)
			
			tableBody += u"""   <tr>
								<td>%s</td>
								<td><a href=http://www.imdb.com/title/%s/ target="_blank">%s</a></td>
								<td>%s</td>
								<td>%s</td>
								<td>
									<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/apply.png" alt="apply" title="apply" /></a>
								</td>
								</tr>
						""" % (entry.Year, entry.ImdbId, entry.ImdbId, entry.Title, entry.IsTVSeries, evtApply)
			
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
		
		return utf8ToLatin(finalOutput)
		
##
#
##		
class AddRecord (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("AddRecord", True)
	
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
		
		tableBody = u""
		
		entries = WebData().getData("options")
		
		for entry in entries:
			print entry
			print entry[1].value
			configType = "text"
			configValue = "value=\"%s\"" % entry[1].value
			tag = "input"
			
			if type(entry[1].value) is bool:
				configType = "checkbox"
				if entry[1].value is True:
					configValue = "checked=\"checked\" value=\"true\""
				else:
					configValue = "checked=\"unchecked\" value=\"false\""
			elif type(entry[1]) is ConfigSelection:
				choices = entry[1].choices
				configType = "select"
				tag = "select"
				configValue = entry[1].value
			
			if tag == "input":
				tag = """<input id="value" name="value" type="%s" size="50" %s></input>""" % (configType, configValue)
			elif tag == "select":
				tag = u"""<select id="value" name="value">"""
				for choice in choices:
					if choice == configValue:
						tag += u"""<option value="%s" size="50" selected>%s</option>""" % (choice, choice)
					else:
						tag += u"""<option value="%s" size="50">%s</option>""" % (choice, choice)
				
				tag += u"""</select>"""
			
			tableBody += u"""
							<form id="saveSetting" action="/action" method="get">
								<input type="hidden" name="method" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_e2"></input>
								<input type="hidden" name="type" value="%s"></input>
								<tr id="tr_entry">
									<td width="300px">%s:</td>
									<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
									<td width="200px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (configType, entry[0], entry[0], tag)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_E2 -->", tableBody)
		
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
		