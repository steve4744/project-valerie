from Components.config import config

from twisted.web.resource import Resource

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.DMC_Global import Update
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebData import WebData
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebHelper import WebHelper
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
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
		global Manager
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		if Manager is None:
			from Plugins.Extensions.ProjectValerieSync.Manager import Manager
			
		finalOutput = WebData().getHtmlCore("Home")
		
		currentVersion = config.plugins.pvmc.version.value
		movieCount = str(Manager().getMoviesCount())
		tvShowCount = str(Manager().getSeriesCount())
		episodeCount = str(Manager().getEpisodesCount())
				
		finalOutput = finalOutput.replace("<!-- CURRENT_VERSION -->", currentVersion)
		
		finalOutput = finalOutput.replace("<!-- MOVIE_COUNT -->", movieCount)
		finalOutput = finalOutput.replace("<!-- TVSHOW_COUNT -->", tvShowCount)
		finalOutput = finalOutput.replace("<!-- EPISODE_COUNT -->", episodeCount)
		
		updateNeeded = Update().checkForUpdate()[0]
		
		if (updateNeeded is None):
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
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Movies")
		
		for entry in entries:
			evtEdit = WebData().getEditString(entry, "isMovie")
			evtDelete = WebData().getDeleteString(entry, "isMovie")
			
			tableBody += u"""   <tr>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
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
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Series")

		for entry in entries:
			evtShowEpisodes = WebData().getEpisodesOfTvShow(entry.Id)
			evtEdit = WebData().getEditString(entry, "isTvShow")
			evtAddEpisode = WebData().getAddEpisodeString(entry, "isEpisode")
			evtDelete = WebData().getDeleteString(entry, "isTvShow") 
			
			tableBody += u"""   <tr>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td><a href=http://thetvdb.com/index.php?tab=series&id=%s target="_blank">%s</a></td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/showEpisodes.png" alt="show Episodes" title="show Episodes" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/add.png" alt="add" title="add" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>						
							</td>
						    </tr>
			""" % (entry.TheTvDbId, entry.Title, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.TheTvDbId, evtShowEpisodes, evtEdit, evtAddEpisode, evtDelete)
		
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
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Episodes")

		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Episodes/Header.tpl")
		tableBody = u""
		
		# get episodes of serie (parentid)
		ParentId = request.args["ParentId"][0]		
		entries = WebData().getData("EpisodesOfSerie", ParentId)
		
		for entry in entries:
			evtEdit = WebData().getEditString(entry, "isEpisode")
			evtDelete = WebData().getDeleteString(entry, "isEpisode")
			
			tableBody += u"""   <tr>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
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
		global MediaInfo
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerieSync.MediaInfo import MediaInfo
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		global Manager
		if Manager is None:
			from Plugins.Extensions.ProjectValerieSync.Manager import Manager
		
		finalOutput = WebData().getHtmlCore("MediaInfo", True)
		
		Id = None
		ParentId = None
		imdbId = u""
		theTvDbId = u""
		mode = request.args["mode"][0]
		
		#Postback error - used for error only ... review
		if mode=="done" or mode=="error":
			return finalOutput
		
		type = request.args["type"][0]

		if mode == 'edit':
			finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Edit Media")
			Id = request.args["Id"][0]
			m = WebData().getData("MediaInfo_"+type, Id)
			imdbId = m.ImdbId
			theTvDbId = m.TheTvDbId
		elif mode == 'addbyimdb':
			finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Add Media")
			m = MediaInfo()
			m.ImdbId = "";
			m.SearchString = "";
			if type == "isEpisode":
				type = "isSerie" # we need to do this because Manger.syncelemnts uses this name not the name till now isTvShow
			
			path = "/PATH/TO/FILE/"
			filename = "FILENAME"
			extension = "EXT"
			if type == "isMovie" or type == "isSerie":
				m.ImdbId = request.args["ImdbId"][0]
				printl("addbyimdb: "+str(request.args["ImdbId"][0]) + " " + str(type))
				syncData = Manager().syncElement(path, filename, extension, m.ImdbId, type)
				m = syncData[0]
		
		elif mode == 'addbytitle':
			finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Add Media")	
			mediainfo.SearchString = request.args["Title"][0]
			results = Manager().searchAlternatives(mediainfo)			
			
			
		#if type == 'isTvShow':
		if "ParentId" in request.args:
			ParentId = request.args["ParentId"][0]
		else:
			ParentId = u""

		image = u""
		backdrop = u""
		if type == "isMovie":
			image = """<img id="duck_img" src="%s" width="78" height="107" alt="n/a"></img>""" % ("/media/" + imdbId + "_poster_195x267.png")
			backdrop = """<img id="duck_backdrop_img" src="%s" width="160" height="90" alt="n/a"></img>""" % ("/media/" + imdbId + "_backdrop_320x180.png")
			
		elif type == "isTvShow" or type == "isEpisode":
			image = """<img id="duck_img" src="%s" width="78" height="107" alt="n/a"></img>""" % ("/media/" + theTvDbId + "_poster_195x267.png")
			backdrop = """<img id="duck_backdrop_img" src="%s" width="160" height="90" alt="n/a"></img>""" % ("/media/" + theTvDbId + "_backdrop_320x180.png")
	
		mediaForm = u"""
		<form action="/action" method="post">
			<input type="hidden" name="type" value=%s>
			<input type="hidden" name="mode" value="edit">
			<input type="hidden" Id="Id" name="Id" value="%s">
			<input type="hidden" Id="ParentId" name="ParentId" value="%s">
			
			<tr><td></td></tr>
			<tr id="tr_type"><td>Type:</td><td id="td_type">
				<input id="type" name="Type" type="text" size="10" value="%s" disabled="disabled"></input>
				<input id="id2" name="id2" type="text" size="10" value="%s" disabled="disabled"></input> </td></tr> 
			<tr id="tr_imdbid"><td>ImdbId:</td><td>
				<input id="imdbid" name="ImdbId" type="text" size="10" value="%s" class="requiredlabel"></input></td><td>(e.g. tt9000000)</td></tr>
			<tr id="tr_thetvdbid"><td>TheTvDbId:</td><td>
				<input id="thetvdbid" name="TheTvDbId" type="text" size="10" value="%s" class="requiredlabel"></input></td><td>(e.g. 999999)</td></tr>
			<tr id="tr_title" class="small requiredlabel"><td>Title:</td><td>
				<input id="title" name="Title" type="text" class="medium requiredfield" value="%s"></input></td><td>(e.g. my title)</td></tr>
			<tr id="tr_tag"><td>Tag:</td><td>
				<input id="tag" name="Tag" type="text" value="%s" class="medium"></input></td><td>(e.g.my tag)</td></tr>
			<tr id="tr_season"><td>Season:</td><td>
				<input id="season" name="Season" type="text"  maxlength="2" value="%s" class="small"></input></td><td>(e.g. 01)</td></tr>
			<tr id="tr_episode"><td>Episode:</td><td>
				<input id="episode" name="Episode" type="text" maxlength="3" value="%s" class="small"></input></td><td>(e.g. 01)</td></tr>
			<tr id="tr_plot"><td>Plot:</td><td>
				<textarea id="plot" name="Plot" cols="50" rows="15" class="medium">%s</textarea></td><td>(e.g. story description)</td></tr>
			<tr id="tr_runtime"><td>Runtime:</td><td>
				<input id="runtime" name="Runtime" type="text" value="%s" class="small"></input></td><td>(e.g. 90)</td></tr>
			<tr id="tr_year"><td>Year:</td><td>
				<input id="year" name="Year" type="text" maxlength="4" value="%s" class="small"></td><td></input>(e.g. 2011)</td></tr>
			<tr id="tr_genres"><td>Genres:</td><td>
				<input id="genres" name="Genres" type="text" value="%s" class="medium"></input></td><td>(e.g. Action|Thriller)</td></tr>
			<tr id="tr_popularity"><td>Popularity:</td><td>
				<!--<input id="popularity" name="Popularity" type="text" value=""></input></td><td>(e.g. 9)-->				
				<select id="popularity" name="Popularity" class="small">	
				%s			
				</select>
				</td></tr>
				
			<tr id="tr_path"><td>Path:</td><td>
				<input class="medium requiredfield" id="path" name="Path" type="text" value="%s"></td><td></input>(e.g. /some/where/on/my/box/)</td></tr>
			<tr id="tr_filename"><td>Filename:</td><td>
				<input class="medium requiredfield"  id="filename" name="Filename" type="text" value="%s"></td><td></input>(e.g. my filename)</td></tr>
			<tr id="tr_extension" class="requiredlabel"><td>Extension:</td><td>
				<input class="small requiredfield"  id="extension" name="Extension" type="text" maxlength="3" value="%s"></td><td></input>(without leading . => e.g. mkv)</td></tr>		
			<tr id="tr_seen"><td>Seen</td><td>
				<input id="seen" name="Seen" type="checkbox" value="1" %s></td><td></input></td></tr>		
			<tr><td>
			<tr><td>
				<input type="submit" value="Save"></input>
			</td></tr>
		</form>
			""" 
		if mode=="add": 
			mediaForm = mediaForm % (type, u"", ParentId, type, u"", u"", u"", u"", u"", u"", u"", u"", u"", u"", u"", u"", u"", u"", u"", 0)
		else:
			seenCheck = ""
			if m.Seen == "1":
				seenCheck = "checked"
			
			mediaForm = mediaForm % (type, m.Id, m.ParentId, type, m.Id, m.ImdbId, m.TheTvDbId, m.Title, m.Tag, m.Season, m.Episode, m.Plot, m.Runtime, m.Year, m.Genres, self.getPopularity(m.Popularity), m.Path, m.Filename, m.Extension, seenCheck)

		finalOutput = finalOutput.replace("<!-- CUSTOM_IMAGE -->", image)
		finalOutput = finalOutput.replace("<!-- CUSTOM_BACKDROP -->", backdrop)
		finalOutput = finalOutput.replace("<!-- CUSTOM_FORM -->", mediaForm)
	
		return utf8ToLatin(finalOutput)

	def getPopularity(self, value):
		str = u""
		str += """<option value="">-- Select --</option>"""
		for i in range(1,11):
			if i==value:
				str += """<option value="%d" selected="yes">%d</option>""" % (i,i)
			else:
				str += """<option value="%d">%d</option>""" % (i,i)
		return str
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
			#entry.oldImdbId = request.args["oldImdbId"][0]
			entry.Id = u"" #request.args["Id"][0]
			
			if request.args["mode"][0] == "existing":
				entry.Path = request.args["Path"][0]
				entry.Filename = request.args["Filename"][0]
				entry.Extension = request.args["Extension"][0]
				existing = "true"
		
			evtApply = WebData().getApplyAlternativeString(entry, existing)
			
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
		
		finalOutput = WebData().getHtmlCore("Options")
				
		return utf8ToLatin(finalOutput)

##
#
##		
class GlobalSetting (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
				
		finalOutput = WebData().getHtmlCore("Options" , True, "Global")
		
		tableBody = self.buildTableGlobal("options.global")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_GLOBAL -->", tableBody)
	
		return utf8ToLatin(finalOutput)	
	
	def buildTableGlobal(self, section):
		tableBody = u""
		entries = WebData().getData(section)
		for entry in entries:
			value = entry[1].value
			
			configType, tag = WebHelper().prepareTable(value, entry[1])
			
			tableBody += u"""
							<form id="saveSetting" action="/action" method="get">
								<input type="hidden" name="mode" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_global"></input>
								<input type="hidden" name="type" value="%s"></input>
								<tr id="tr_entry">
									<td width="550px">%s:</td>
									<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
									<td width="200px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (configType, entry[0], entry[0], tag)
		
		return tableBody

##
#
##		
class SyncSettings (Resource):
	def render_GET(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		
		finalOutput = WebData().getHtmlCore("Options" , True, "Sync")
						
		tableBody = self.buildTableSyncFileTypes("options.sync")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_SYNC_FILETYPES -->", tableBody)
		
		tableBody = self.buildTableSyncPath("options.sync")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_SYNC_PATH -->", tableBody)
	
		return utf8ToLatin(finalOutput)

	def buildTableSyncFileTypes(self, section):
		tableBody = u""
		pathsConfig = WebData().getData(section)
		
		name = u"FileTypes"
		value = '|'.join(pathsConfig.getFileTypes())
		configType, tag = WebHelper().prepareTable(value, None)
		
		tableBody += u"""
						<table align="left" id="settings_sync">
								<form id="saveSetting" action="/action" method="get">
									<input type="hidden" name="mode" value="options.saveconfig"></input>
									<input type="hidden" name="what" value="settings_sync"></input>
									<input type="hidden" name="section" value="filetypes"></input>
									<input type="hidden" name="type" value="%s"></input>
									<tr id="tr_entry">
										<td width="100px">%s:</td>
										<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
										<td width="700px">%s</td>
										<td width="70px"><input type="submit" value="save"></input></td>
									</tr>
								</form>
							</table>
				""" % (configType, name, name, tag)
		
		return tableBody
		
	def buildTableSyncPath(self, section):
		tableBody = u""
		pathsConfig = WebData().getData(section)
		
		tableBody += u"""<table align="left" id="settings_sync_sub">"""
		tableBody += u"""<tr>
							<td width="100px">Enabled</td>
							<td width="5100px">Directory</td>
							<td width="50px">Type</td>
							<td width="50px">UseFolder</td>
							<td width="70px"></td>
						</tr>"""
		
		for path in pathsConfig.getPaths():
			name = u"Directory"
			value = path["directory"]
			id = path["directory"]
			
			configType, tag = WebHelper().prepareTable(value, None)
			
			types = (path["type"], pathsConfig.getPathsChoices()["type"], )
			
			
			tableBody += u"""
							<form id="saveSetting" action="/action" method="get">
								<input type="hidden" name="mode" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_sync"></input>
								<input type="hidden" name="section" value="paths"></input>
								<input type="hidden" name="Id" value="%s"></input>
								<tr id="tr_entry">
									<td width="50px">%s</td>
									<td width="200px">%s</td>
									<td width="50px">%s</td>
									<td width="50px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (id, WebHelper().prepareTable(path["enabled"], None, "enabled")[1], WebHelper().prepareTable(path["directory"], None, "directory")[1], 
									WebHelper().prepareTable(types, None, "type")[1], WebHelper().prepareTable(path["usefolder"], None, "usefolder")[1])
		
		tableBody += u"""</table>"""
		
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
		