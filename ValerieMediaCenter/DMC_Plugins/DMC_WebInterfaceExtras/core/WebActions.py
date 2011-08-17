from Components.config import config

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebData import WebData
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebHelper import WebHelper
from twisted.web.resource import Resource

import urllib
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
MobileImdbComProvider = None
MediaInfo = None
# --- LAZY IMPORTS ---

##
#
##
class WebActions(Resource):

	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)

	def action(self, request):
		global Manager
		global utf8ToLatin
		global MediaInfo
		if Manager is None:
			from Plugins.Extensions.ProjectValerieSync.Manager import Manager
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerieSync.MediaInfo import MediaInfo
		
		printl("request: " + str(request), self)
		printl("request.args: " + str(request.args), self)
		printl("request.args[method]: " + str(request.args["method"]), self)
		
		##
		# extras section
		##
		if request.args["method"][0] == "backup":
			import zipfile, os

			zipf = zipfile.ZipFile('/hdd/valerie-backup.zip', mode='w', compression=zipfile.ZIP_STORED )
			path = utf8ToLatin(config.plugins.pvmc.tmpfolderpath.value)
			WebHelper().recursive_zip(zipf, path)
			zipf.close()

			return WebHelper().redirectMeTo("/elog/valerie-backup.zip")	

		elif request.args["method"][0] == "restore":
			#http://webpython.codepoint.net/cgi_file_upload
			outputStream = open(filename, '/hdd/test.zip')
			outputStream.write(request.args['myFile'])
			outputStream.close()
			
		
		##
		# add section	
		##
		elif request.args["method"][0] == "add":
			# add movies
			manager = Manager()				
			key_value_dict = {}				
			for key in request.args.keys():
				key_value_dict[key] = request.args[key][0]
			
			if request.args["what"][0] == "isMovie":
				result = manager.insertMedia(Manager.MOVIES, key_value_dict)
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=movies")
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=movies")
			
			# add tvshows
			elif request.args["what"][0] == "isTvShow":
				result = manager.insertMedia(Manager.TVSHOWS, key_value_dict)
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=tvshows")	
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=tvshows")	
			
			# add tvshowepisodes
			elif request.args["what"][0] == "isEpisode":
				printl ("INSERT: " + str(key_value_dict))
				result = manager.insertMedia(Manager.TVSHOWSEPISODES, key_value_dict)				
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=episodes&ParentId=" + request.args["ParentId"][0])
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=episodes&ParentId=" + request.args["ParentId"][0])
		
		##
		# edit section	
		##
		elif request.args["method"][0] == "edit":
			# edit movies
			manager = Manager()
			key_value_dict = {}				
			for key in request.args.keys():
				key_value_dict[key] = request.args[key][0]
					
			if request.args["what"][0] == "isMovie":
				result = manager.updateMedia(Manager.MOVIES, key_value_dict)
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=movies&Id=" + request.args["Id"][0])
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=movies&Id=" + request.args["Id"][0])
			
			# edit tvshows
			elif request.args["what"][0] == "isTvShow":
				result = manager.updateMedia(Manager.TVSHOWS, key_value_dict)
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=tvshows&Id=" + request.args["Id"][0])
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=tvshows&Id=" + request.args["Id"][0])
			
			# edit tvsshowepisodes
			elif request.args["what"][0] == "isEpisode":
				result = manager.updateMedia(Manager.TVSHOWSEPISODES, key_value_dict)
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=episodes&ParentId="+request.args["ParentId"][0]+"&Id=" + request.args["Id"][0])
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=episodes&&ParentId="+request.args["ParentId"][0]+"&Id=" + request.args["Id"][0])
		
		##
		# delete section
		##
		elif request.args["method"][0] == "delete":
			manager = Manager()
			#key_value_dict = {}				
			#for key in request.args.keys():
			#	key_value_dict[key] = request.args[key][0]
			
			if request.args["what"][0] == "isMovie":
				result = manager.deleteMedia(Manager.MOVIES, request.args["Id"][0])
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=movies")
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=movies")
				
		# delete tvshowepisodes
			elif request.args["what"][0] == "isEpisode":
				result = manager.deleteMedia(Manager.TVSHOWSEPISODES, request.args["Id"][0])
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=episodes&ParentId="+request.args["ParentId"][0]+"&Id=" + request.args["Id"][0])
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=episodes&ParentId="+request.args["ParentId"][0]+"&Id=" + request.args["Id"][0])
				
		# delete tvshow		
			elif request.args["what"][0] == "isTvShow":
				result = manager.deleteMedia(Manager.TVSHOWS, request.args["Id"][0])
				if result:
					return WebHelper().redirectMeTo("/mediainfo?mode=done&target=tvshows")
				else:
					return WebHelper().redirectMeTo("/mediainfo?mode=error&target=tvshows")
		
		##
		# option section
		##
		elif request.args["method"][0] == "options.saveconfig":
			if request.args["what"][0] == "settings_global":
				name = request.args["name"][0]
				value = "unchecked"
				if request.args.has_key("value"):
					value = request.args["value"][0]
				
				valueType = request.args["type"][0]
				
				printl("name=\"%s\" value=\"%s\" type=\"%s\"" % (name, value, valueType), self, "D")
				
				entries = WebData().getData("options.global")
				for entry in entries:
					if entry[0] == name:
						if valueType == "text" or valueType == "select":
							printl("Setting \"%s\" to \"%s\"" % (name, value), self, "I")
							entry[1].value = value
						elif valueType == "checkbox":
							if value == "checked" or value == "on":
								value = True
							else:
								value = False
							printl("Setting \"%s\" to \"%s\"" % (name, value), self, "I")
							entry[1].value = value
						entry[1].save()
			
			elif request.args["what"][0] == "settings_sync":
				if request.args["section"][0] == "paths":
					id = request.args["Id"][0]
					directory = request.args["directory"][0]
					typeFolder = request.args["type"][0]
					enabled = request.args.has_key("enabled")
					useFolder = request.args.has_key("usefolder")
					
					path = {"directory": directory, "enabled": enabled, "usefolder": useFolder, "type": typeFolder}
					
					from Plugins.Extensions.ProjectValerieSync.PathsConfig import PathsConfig
					PathsConfig().getInstance().setPath(id, path)
					PathsConfig().getInstance().save()
				
				elif request.args["section"][0] == "filetypes":
					value = request.args["value"][0]
					from Plugins.Extensions.ProjectValerieSync.PathsConfig import PathsConfig
					PathsConfig().getInstance().setFileTypes(value.split("|"))
					PathsConfig().getInstance().save()
			
			return WebHelper().redirectMeTo("/options")
		
		##
		# collecting data
		##	
		elif request.args["method"][0] == "collectData":
			if request.args["usePath"][0] == "true":
				path = request.args["Path"][0]
				filename = request.args["Filename"][0]
				extension = request.args["Extension"][0]
			else:
				path = "/PATH/TO/FILE/"
				filename = "FILENAME"
				extension = "EXT"
			
			mediainfo = MediaInfo()
			mediainfo.ImdbId = "";
			mediainfo.SearchString = "";
			
			type = request.args["type"][0]
			if type == "isEpisode":
				type = "isSerie" # we need to do this because Manger.syncelemnts uses this name not the name till now isTvShow
			
			if type == "isMovie" or type == "isSerie":

				if request.args["by"][0] == "ImdbId":
					mediainfo.ImdbId = request.args["ImdbId"][0]
					syncData = Manager().syncElement(path, filename, extension, mediainfo.ImdbId, type)
					result = syncData[0]
				
				elif request.args["by"][0] == "Title":
					mediainfo.SearchString = request.args["Title"][0]
					results = Manager().searchAlternatives(mediainfo)
					
				else:
					pass
			
			elif type == "TvShow":
				return WebHelper().redirectMeTo("/")
			
			
			redirectString = "mediainfo?"
			redirectString += "useData=true&"
			redirectString += "usePath=" + request.args["usePath"][0] + "&"
			redirectString += "type=" + request.args["type"][0] + "&"
			if request.args["oldImdbId"][0] == "-1":
				redirectString += "mode=new_record&"
			else:
				redirectString += "mode=change_imdbid&"
				redirectString += "oldImdbId=" + request.args["oldImdbId"][0] + "&"
			redirectString += "ImdbId=" + urllib.quote(str(mediainfo.ImdbId)) + "&"
			redirectString += "TheTvDbId=" + urllib.quote(str(result.TheTvDbId)) + "&"
			redirectString += "Title=" + urllib.quote(str(result.Title)) + "&"
			redirectString += "Season= " + urllib.quote(str(result.Season)) + "&"
			redirectString += "Episode=" + urllib.quote(str(result.Episode)) + "&"
			redirectString += "Plot=" + urllib.quote(str(result.Plot))+ "&"
			redirectString += "Runtime=" + urllib.quote(str(result.Runtime)) + "&"
			redirectString += "Year=" + urllib.quote(str(result.Year)) + "&"
			redirectString += "Genres=" + urllib.quote(str(result.Genres)) + "&"
			redirectString += "Tag=" + urllib.quote(str(result.Tag)) + "&"
			redirectString += "Popularity=" + urllib.quote(str(result.Popularity)) + "&"
			redirectString += "Poster=" + urllib.quote(str(result.Poster)) + "&"
			redirectString += "Backdrop=" + urllib.quote(str(result.Backdrop)) + "&"			
			if request.args["usePath"][0] == "true":
				redirectString += "Path=" + urllib.quote(str(path)) + "&"
				redirectString += "Filename=" + urllib.quote(str(filename)) + "&"
				redirectString += "Extension=" + urllib.quote(str(extension))
			
			
			return WebHelper().redirectMeTo(redirectString)
		
		##
		# alter arts
		##	
		elif request.args["method"][0] == "change_arts":
			manager = Manager()
			type = request.args["type"][0]
			media_source = request.args["media_source"][0]
			media_type = request.args["media_type"][0]
			id = request.args["Id"][0]

			
			if type == "isMovie":
				t = Manager.MOVIES
				#primary_key = {}
				#primary_key["imdbid"] = request.args["ImdbId"][0]
			
			elif type == "isTvShow":
				t = Manager.TVSHOWS
				#primary_key = {}
				#primary_key["thetvdbid"] = request.args["TheTvDbId"][0]
				
			elif type == "isEpisode":
				t = Manager.TVSHOWSEPISODES
				#primary_key = {}
				#primary_key["thetvdbid"] = request.args["TheTvDbId"][0]
				#primary_key["season"] = request.args["Season"][0]
				#primary_key["episode"] = request.args["Episode"][0]
			
			else:
				return utf8ToLatin("error")
			
			
			if media_type == "poster":
				#result = manager.getArtsByUsingPrimaryKey(t, primary_key, True, None, media_source)
				result = manager.changeMediaArts(t, id, True, None, media_source)
				if result == True:
					return utf8ToLatin("success")
				else:
					return utf8ToLatin("error")
			
			elif media_type == "backdrop":
				#result = manager.getArtsByUsingPrimaryKey(t, primary_key, True, media_source, None)
				result = manager.changeMediaArts(t, id, True, media_source, None)
				if result == True:
					return utf8ToLatin("success")
				else:
					return utf8ToLatin("error")
			else:
				printl("no media type found", self)
				return utf8ToLatin("error")
			
			return utf8ToLatin("error")
		
		##
		# save to db
		##	
		elif request.args["method"][0] == "save_changes_to_db":
			manager = Manager()
			manager.finish()
			
			if request.args["return_to"][0] == "movies":
				return WebHelper().redirectMeTo("/movies")
			elif request.args["return_to"][0] == "tvshows":
				return WebHelper().redirectMeTo("/tvshows")
			elif request.args["return_to"][0] == "episodes":
				return WebHelper().redirectMeTo("/episodes")					
		
		##
		# dump db to dumps - view via webif http://url:8888/dumps
		##	
		elif request.args["method"][0] == "dump_db":
			Manager().getDbDump()
			return WebHelper().redirectMeTo("/movies")					
				