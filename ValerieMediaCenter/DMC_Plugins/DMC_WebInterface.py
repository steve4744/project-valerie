# -*- coding: utf-8 -*-

#http://twistedmatrix.com/documents/current/web/howto/web-in-60/index.html

from   threading import Thread

from Components.config import config
from Components.config import ConfigInteger
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

gAvailable = False
try:
	from twisted.web.server import Site
	from twisted.web.static import File
	from twisted.internet   import reactor, threads
	from twisted.web.resource import Resource
	
	from Plugins.Extensions.ProjectValerieSync.Manager import Manager
	from Plugins.Extensions.ProjectValerieSync.Utf8 import *
	
	import cgi
	
	gAvailable = True
except:
	gAvailable = False

config.plugins.pvmc.plugins.webinterface = ConfigSubsection()
config.plugins.pvmc.plugins.webinterface.port = ConfigInteger(default = 8888, limits=(1, 65535) )

class Action(Resource):

	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)

	def action(self, request):
		printl("request: " + str(request), self)
		printl("request.args: " + str(request.args), self)
		printl("request.args[type]: " + str(request.args["type"]), self)
		
		# Here we can react to different request
		# After a request has been processed we can display a request specific answer
		# For example, after requesting alternatives for a move we should return them instead of the 
		#  Refresh html page you see below as default answer
		if request.args["type"][0] == "add":
			if request.args["what"][0] == "movies":
				key_value_dict = {}
				for key in request.args.keys():
					key_value_dict[key] = request.args[key][0]
				
				primary_key = {}
				primary_key["imdbid"] = request.args["imdbid"][0]
				
				manager = Manager()
				manager.start()
				manager.addByUsingPrimaryKey(Manager.MOVIES, primary_key, key_value_dict)
				manager.finish()
				return self.redirect("/static/test.html")
			
		elif request.args["type"][0] == "edit":
			if request.args["what"][0] == "movies":
				key_value_dict = {}
				for key in request.args.keys():
					key_value_dict[key] = request.args[key][0]
				
				primary_key = {}
				primary_key["imdbid"] = request.args["imdbid"][0]
				
				manager = Manager()
				manager.start()
				manager.replaceByUsingPrimaryKey(Manager.MOVIES, primary_key, key_value_dict)
				manager.finish()
				return self.redirect("/static/test.html")
		
		elif request.args["type"][0] == "delete":
			if request.args["what"][0] == "movies":
				primary_key = {}
				primary_key["imdbid"] = request.args["imdbid"][0]
				
				manager = Manager()
				manager.start()
				manager.removeByUsingPrimaryKey(Manager.MOVIES, primary_key)
				manager.finish()
				return self.redirect("/static/test.html")

		elif request.args["type"][0] == "alternatives":
			pass
		elif request.args["type"][0] == "get":
			
			manager = Manager()
			manager.start()
			
			json = "{\n\"page\": 1, \"total\": 2, \"rows\": [\n"
			
			if request.args["what"][0] == "movies":
				entries = manager.getAll(Manager.MOVIES)
				for entry in entries:
					json += u"{\n"
					json += u"\"title\": \"" + entry.Title + "\",\n"
					json += u"\"year\": " + str(entry.Year) + ",\n"
					json += u"\"imdbid\": \"" + entry.ImdbId + "\",\n"
					json += u"\"file\": \"" + entry.Filename + u"." + entry.Extension + "\",\n"
					json += u"},\n"
			
			elif request.args["what"][0] == "tvshows":
				entries = manager.getAll(Manager.TVSHOWS)
				for entry in entries:
					json += u"{\n"
					json += u"\"title\": \"" + entry.Title + "\",\n"
					json += u"\"year\": " + str(entry.Year) + ",\n"
					json += u"\"imdbid\": \"" + entry.ImdbId + "\",\n"
					json += u"\"thetvdbid\": \"" + entry.TheTvDbId + "\",\n"
					json += u"},\n"
			
			elif request.args["what"][0] == "tvshowsepisodes":
				entries = manager.getAll(Manager.TVSHOWSEPISODES)
				for entry in entries:
					json += u"{\n"
					json += u"\"title\": \"" + entry.Title + "\",\n"
					json += u"\"season\": " + str(entry.Season) + ",\n"
					json += u"\"episode\": " + str(entry.Episode) + ",\n"
					json += u"\"year\": " + str(entry.Year) + ",\n"
					json += u"\"imdbid\": \"" + entry.ImdbId + "\",\n"
					json += u"\"thetvdbid\": \"" + entry.TheTvDbId + "\",\n"
					json += u"\"file\": \"" + entry.Filename + u"." + entry.Extension + "\",\n"
					json += u"},\n"
			
			elif request.args["what"][0] == "failed_all":
				entries = manager.getAll(Manager.FAILED_ALL)
				for entry in entries:
					json += u"{\n"
					json += u"\"file\": \"" + entry.Path + u"/" + entry.Filename + u"." + entry.Extension + "\",\n"
					json += u"\"cause\": \"" + entry.CauseStr + "\",\n"
					json += u"\"description\": \"" + entry.Description + "\",\n"
					json += u"},\n"
			
			json = json[:len(json)-2]
			json += "\n]\n}\n}\n"
			
			return utf8ToLatin(json)

	def redirect(self, url):
		return """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta HTTP-EQUIV="REFRESH" content="0; url=%s">
</head>
<body>
</body>
</html>""" % url

class Index(Resource):
	def render_GET(self, request):
		f = Utf8(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterface/index.html", "r")
		html = f.read()
		f.close()
		
		m = Utf8(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterface/static/mainmenu.tpl", "r")
		mainmenu = m.read()
		m.close()
		
		html = html.replace("<!-- REPLACE_MAINMENU -->", mainmenu)
		
		c = Utf8(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterface/static/about.tpl", "r")
		content = c.read()
		c.close()
		
		html = html.replace("<!-- REPLACE_CONTENT -->", content)

		return utf8ToLatin(html)

class Database(Resource):
	def __init__(self, type):
		self.type = type

	def render_GET(self, request):

		#TODO: We should cache these
		manager = Manager()
		manager.start()
		
		thead = u""
		tbody = u""
		alt = False
		if self.type == "movies":
			entries = manager.getAll(Manager.MOVIES)
		elif self.type == "tvshows":
			entries = manager.getAll(Manager.TVSHOWS)
		elif self.type == "tvshowepisodes":
			entries = manager.getAll(Manager.TVSHOWSEPISODES)
		elif self.type == "failed_all":
			entries = manager.getAll(Manager.FAILED_ALL)
		
		### <!-- REPLACE_THEAD -->
		if self.type == "movies":
			thead += """
        <th width="65px">Poster</th>
        <th class="sortfirstasc">Name</th>
        <th width="40px">Year</th>
        <th width="100px">ImdbId</th>
        <th>File</th>"""
		elif self.type == "tvshows":
			thead += """
        <th width="65px">Poster</th>
        <th class="sortfirstasc">Name</th>
        <th width="30px">Season</th>
        <th width="30px">Episode</th>
        <th width="40px">Year</th>
        <th width="100px">ImdbId</th>
        <th width="70px">TheTvDbId</th>
        <th>File</th>"""
		elif self.type == "tvshowepisodes":
			thead += """
        <th width="65px">Poster</th>
        <th class="sortfirstasc">Name</th>
        <th width="30px">Season</th>
        <th width="30px">Episode</th>
        <th width="40px">Year</th>
        <th width="100px">ImdbId</th>
        <th width="70px">TheTvDbId</th>
        <th>File</th>"""
		elif self.type == "failed_all":
			thead += """
        <th class="sortfirstasc">File</th>
        <th width="100px">Cause</th>
        <th>Description</th>"""
		
		### <!-- REPLACE_TBODY -->
		for entry in entries:
			if alt:
				altString = "class=\"alt\""
			else:
				altString = ""
			if self.type == "movies":
				tbody += u"""      <tr %s>
        <td><img src=\"http://val.duckbox.info/convertImg/poster/%s.png\" width="78" height="107" alt="n/a"></img></td>
        <td>%s</td>
        <td>%d</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
""" % (altString, entry.ImdbId, entry.Title, entry.Year, entry.ImdbId, entry.Filename + u"." + entry.Extension)
			elif self.type == "tvshows":
				tbody += u"""      <tr id=%s>
        <td><img src=\"http://val.duckbox.info/convertImg/poster/%s.png\" width="78" height="107" alt="n/a"></img></td>
        <td>%s</td>
        <td>%d</td>
        <td>%d</td>
        <td>%d</td>
        <td>%s</td>
        <td><a href=http://thetvdb.com/index.php?tab=series&id=%s target="_blank">%s</a></td>
        <td>%s</td>
      </tr>
""" % (altString, entry.TheTvDbId, entry.Title, entry.Season, entry.Episode, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.TheTvDbId, entry.Filename + u"." + entry.Extension)
			elif self.type == "tvshowepisodes":
				tbody += u"""      <tr %s>
        <td><img src=\"http://val.duckbox.info/convertImg/poster/%s.png\" width="78" height="107" alt="n/a"></img></td>
        <td>%s</td>
        <td>%d</td>
        <td>%d</td>
        <td>%d</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
""" % (altString, entry.TheTvDbId, entry.Title, entry.Season, entry.Episode, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.Filename + u"." + entry.Extension)
			elif self.type == "failed_all":
				tbody += u"""      <tr %s>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
""" % (altString, entry.Path + u"/" + entry.Filename + u"." + entry.Extension, entry.CauseStr, entry.Description)
			alt = not alt
		
		
		f = Utf8(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterface/index.html", "r")
		html = f.read()
		f.close()
		
		m = Utf8(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterface/static/mainmenu.tpl", "r")
		mainmenu = m.read()
		m.close()
		
		html = html.replace("<!-- REPLACE_MAINMENU -->", mainmenu)
		
		c = Utf8(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterface/static/browsetable.tpl", "r")
		content = c.read()
		c.close()
		
		html = html.replace("<!-- REPLACE_CONTENT -->", content)
		
		
		html = html.replace("<!-- REPLACE_THEAD -->", thead)
		html = html.replace("<!-- REPLACE_TBODY -->", tbody)
		
		return utf8ToLatin(html)

def autostart(session):
	try:
		root = Resource()
		
		#Dynamic Pages
		root.putChild("", Index())
		root.putChild("movies", Database("movies"))
		root.putChild("tvshows", Database("tvshows"))
		root.putChild("tvshowepisodes", Database("tvshowepisodes"))
		root.putChild("failed_all", Database("failed_all"))
		
		#Static Pages, CsS, JS
		root.putChild("static", File(utf8ToLatin(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterface/static"), defaultType="text/plain"))
		
		#Folder Lists
		root.putChild("vlog", File('/tmp/valerie/log', defaultType="text/plain"))
		root.putChild("elog", File('/hdd/', defaultType="text/plain"))
		
		#Action pages
		root.putChild("action", Action())
		
		site = Site(root)
		port = config.plugins.pvmc.plugins.webinterface.port.value
		reactor.listenTCP(port, site, interface="0.0.0.0")
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)

def settings():
	s = []
	s.append((_("Port"), config.plugins.pvmc.plugins.webinterface.port, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(name=_("WebInterface"), fnc=settings, where=Plugin.SETTINGS))
	#registerPlugin(Plugin(name=_("WebInterface"), fnc=autostart, where=Plugin.AUTOSTART))
	registerPlugin(Plugin(name=_("WebInterface"), fnc=autostart, where=Plugin.AUTOSTART_E2))
