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
			evtAddEpisode = WebData().getAddEpisodeString(entry, "isEpisode")
			## COMMENT
			#  not active at the moment because we do not check if there are still episodes in db
			#  another thing to solve is that a tvshow needs a path/extension/filename too
			##
			#evtDelete = WebData().getDeleteString(entry, "isTvShow") 
			
			tableBody += u"""   <tr>
							<td><img src=\"http://val.duckbox.info/convertImg2/poster/%s_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%d</td>
							<td>%s</td>
							<td><a href=http://thetvdb.com/index.php?tab=series&id=%s target="_blank">%s</a></td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/showEpisodes.png" alt="show Episodes" title="show Episodes" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/add.png" alt="add" title="add" /></a>
							</td>
						    </tr>
			""" % (entry.TheTvDbId, entry.Title, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.TheTvDbId, evtShowEpisodes, evtEdit, evtAddEpisode)
		
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
			entry.oldImdbId = request.args["oldImdbId"][0]
			
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
						""" % (entry.Year, entry.ImdbId, entry.ImdbId, utf8ToLatin(entry.Title), entry.IsTVSeries, evtApply)
			
		
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
		
		tableBody = self.buildTableGlobal("options.global")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_GLOBAL -->", tableBody)
		
		tableBody = self.buildTableSync("options.sync")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_SYNC -->", tableBody)
		
		return utf8ToLatin(finalOutput)

	def prepareTable(self, value, entry, name="value"):
		
		#print type(value), value
		
		
		tag = "input"
		configType = "text"
		
		if type(value) is bool:
			configType = "checkbox"
			if value is True:
				configValue = "checked=\"checked\""
			else:
				configValue = ""
		elif type(value) is list or type(value) is tuple:
			choices = value[1]
			configType = "select"
			tag = "select"
			configValue = value[0]
		elif type(entry) is ConfigSelection:
			choices = entry.choices
			configType = "select"
			tag = "select"
			configValue = value
		else:
			configValue = "value=\"%s\"" % value
		
		if tag == "input":
			tag = """<input id="value" name="%s" type="%s" size="50" %s></input>""" % (name, configType, configValue)
		elif tag == "select":
			tag = u"""<select id="value" name="%s">""" % name
			for choice in choices:
				if choice == configValue:
					tag += u"""<option value="%s" size="50" selected>%s</option>""" % (choice, choice)
				else:
					tag += u"""<option value="%s" size="50">%s</option>""" % (choice, choice)
			
			tag += u"""</select>"""
		return (configType, tag, )

	def buildTableGlobal(self, section):
		tableBody = u""
		entries = WebData().getData(section)
		for entry in entries:
			value = entry[1].value
			
			configType, tag = self.prepareTable(value, entry[1])
			
			tableBody += u"""
							<form id="saveSetting" action="/action" method="get">
								<input type="hidden" name="method" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_global"></input>
								<input type="hidden" name="type" value="%s"></input>
								<tr id="tr_entry">
									<td width="300px">%s:</td>
									<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
									<td width="200px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (configType, entry[0], entry[0], tag)
		
		return tableBody

	def buildTableSync(self, section):
		tableBody = u""
		pathsConfig = WebData().getData(section)
		
		name = u"FileTypes"
		value = '|'.join(pathsConfig.getFileTypes())
		configType, tag = self.prepareTable(value, None)
		
		tableBody += u"""
						<form id="saveSetting" action="/action" method="get">
							<input type="hidden" name="method" value="options.saveconfig"></input>
							<input type="hidden" name="what" value="settings_sync"></input>
							<input type="hidden" name="section" value="filetypes"></input>
							<input type="hidden" name="type" value="%s"></input>
							<tr id="tr_entry">
								<td width="300px">%s:</td>
								<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
								<td width="200px">%s</td>
								<td width="70px"><input type="submit" value="save"></input></td>
							</tr>
						</form>
				""" % (configType, name, name, tag)
		
		tableBody += u"""<tr id="tr_entry">
									<td width="50px">Paths</td>
									<td width="200px"></td>
									<td width="50px"></td>
									<td width="50px"></td>
									<td width="70px"></td>
								</tr>"""
		
		tableBody += u"""<table align="center" id="settings_sync_sub">"""
		tableBody += u"""<thead>
									<td width="50px">Enabled</td>
									<td width="200px">Directory</td>
									<td width="50px">Type</td>
									<td width="50px">UseFolder</td>
									<td width="70px"></td>
								</thead>"""
		
		tableBody += u"""<tbody>"""
		
		for path in pathsConfig.getPaths():
			name = u"Directory"
			value = path["directory"]
			id = path["directory"]
			
			configType, tag = self.prepareTable(value, None)
			
			types = (path["type"], pathsConfig.getPathsChoices()["type"], )
			
			
			tableBody += u"""
							<form id="saveSetting" action="/action" method="get">
								<input type="hidden" name="method" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_sync"></input>
								<input type="hidden" name="section" value="paths"></input>
								<input type="hidden" name="id" value="%s"></input>
								<tr id="tr_entry">
									<td width="50px">%s</td>
									<td width="200px">%s</td>
									<td width="50px">%s</td>
									<td width="50px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (id, self.prepareTable(path["enabled"], None, "enabled")[1], self.prepareTable(path["directory"], None, "directory")[1], 
									self.prepareTable(types, None, "type")[1], self.prepareTable(path["usefolder"], None, "usefolder")[1])
		
		tableBody += u"""</tbody>"""
		
		return tableBody

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
		