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
		printl("request.args[method]: " + str(request.args["method"]), self)
		
		##
		# add section	
		##
		if request.args["method"][0] == "add":
			# add movies
			if request.args["what"][0] == "movies":
				key_value_dict = {}
				for key in request.args.keys():
					key_value_dict[key] = request.args[key][0]
				
				primary_key = {}
				primary_key["imdbid"] = request.args["imdbid"][0]
				
				manager = Manager()
				manager.start()
				manager.addByUsingPrimaryKey(Manager.MOVIES, primary_key, key_value_dict)
				return self.redirect("/static/edit.html?done")
			
			# add tvshows
			elif request.args["what"][0] == "tvshows":
				key_value_dict = {}
				for key in request.args.keys():
					key_value_dict[key] = request.args[key][0]
				
				primary_key = {}
				primary_key["thetvdbid"] = request.args["thetvdbid"][0]
				
				manager = Manager()
				manager.start()
				manager.addByUsingPrimaryKey(Manager.TVSHOWS, primary_key, key_value_dict)
				return self.redirect("/static/edit.html?done")	
			
			# add tvshowepisodes
			elif request.args["what"][0] == "tvshowepisodes":
				key_value_dict = {}
				for key in request.args.keys():
					key_value_dict[key] = request.args[key][0]
				
				primary_key = {}
				primary_key["thetvdbid"] = request.args["thetvdbid"][0]
				primary_key["season"] = request.args["season"][0]
				primary_key["episode"] = request.args["episode"][0]
				
				manager = Manager()
				manager.start()
				manager.addByUsingPrimaryKey(Manager.TVSHOWSEPISODES, primary_key, key_value_dict)
				return self.redirect("/static/edit.html?done")
		
		##
		# edit section	
		##
		elif request.args["method"][0] == "edit":
			# edit movies
			if request.args["what"][0] == "movies":
				key_value_dict = {}
				for key in request.args.keys():
					key_value_dict[key] = request.args[key][0]
				
				primary_key = {}
				primary_key["imdbid"] = request.args["imdbid"][0]
				
				manager = Manager()
				manager.start()
				manager.replaceByUsingPrimaryKey(Manager.MOVIES, primary_key, key_value_dict)
				return self.redirect("/static/edit.html?done")
			
			# edit tvshows
			elif request.args["what"][0] == "tvshows":
				key_value_dict = {}
				for key in request.args.keys():
					key_value_dict[key] = request.args[key][0]
				
				primary_key = {}
				primary_key["thetvdbid"] = request.args["thetvdbid"][0]
				
				manager = Manager()
				manager.start()
				manager.replaceByUsingPrimaryKey(Manager.TVSHOWS, primary_key, key_value_dict)
				return self.redirect("/static/edit.html?done")
			
			# edit tvshowepisodes
			elif request.args["what"][0] == "tvshowepisodes":
				key_value_dict = {}
				for key in request.args.keys():
					key_value_dict[key] = request.args[key][0]
				
				primary_key = {}
				primary_key["thetvdbid"] = request.args["thetvdbid"][0]
				primary_key["season"] = request.args["season"][0]
				primary_key["episode"] = request.args["episode"][0]
				
				manager = Manager()
				manager.start()
				manager.replaceByUsingPrimaryKey(Manager.TVSHOWSEPISODES, primary_key, key_value_dict)
				return self.redirect("/static/edit.html?done")
		
		##
		# delete section
		##
		elif request.args["method"][0] == "delete":
			if request.args["what"][0] == "movies":
				primary_key = {}
				primary_key["imdbid"] = request.args["imdbid"][0]
				
				manager = Manager()
				manager.start()
				manager.removeByUsingPrimaryKey(Manager.MOVIES, primary_key)
				#manager.finish()
				return self.redirect("/static/edit.html?done")
		
		
		##
		# save to db
		##	
		elif request.args["method"][0] == "save_changes_to_db":
			manager = Manager()
			manager.start()
			manager.finish()
			
			if request.args["return_to"][0] == "movies":
				return self.redirect("/movies")
			elif request.args["return_to"][0] == "tvshows":
				return self.redirect("/tvshows")
			elif request.args["return_to"][0] == "tvshowepisodes":
				return self.redirect("/tvshowepisodes")
		
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
        <th>File</th>
        <th>Actions</th>
        """
		elif self.type == "tvshows":
			thead += """
        <th width="65px">Poster</th>
        <th class="sortfirstasc">Name</th>
        <th width="40px">Year</th>
        <th width="100px">ImdbId</th>
        <th width="70px">TvDbId</th>
        <th>File</th>
        <th>Actions</th>
        """
		elif self.type == "tvshowepisodes":
			thead += """
        <th width="65px">Poster</th>
        <th class="sortfirstasc">Name</th>
        <th width="30px">Season</th>
        <th width="30px">Episode</th>
        <th width="40px">Year</th>
        <th width="100px">ImdbId</th>
        <th width="70px">TvDbId</th>
        <th>File</th>
        <th>Actions</th>
        """
		elif self.type == "failed_all":
			thead += """
        <th class="sortfirstasc">File</th>
        <th width="100px">Cause</th>
        <th>Description</th>"""
		
		
		
		### <!-- REPLACE_TBODY -->
		for entry in entries:
			
			### <!-- string cleanup -->
			entry.Plot = self.clean_strings(entry.Plot)
			entry.Tag = self.clean_strings(entry.Tag)
			
			### <!-- build edit string -->
			onclick_edit  = "javascript:$('#sm_save').show();window.open('/static/edit.html?"
			onclick_edit  += str(self.type) + "&"
			onclick_edit  += str(entry.ImdbId) + "&"
			onclick_edit  += str(entry.TheTvDbId) + "&"
			onclick_edit  += str(entry.Title) + "&"
			onclick_edit  += str(entry.Season) + "&"
			onclick_edit  += str(entry.Episode) + "&"
			onclick_edit  += str(entry.Plot) + "&"
			onclick_edit  += str(entry.Runtime) + "&"
			onclick_edit  += str(entry.Year) + "&"
			onclick_edit  += str(entry.Genres) + "&"
			onclick_edit  += str(entry.Tag) + "&"
			onclick_edit  += str(entry.Popularity) + "&"
			onclick_edit  += str(entry.Path) + "&"
			onclick_edit  += str(entry.Filename) + "&"
			onclick_edit  += str(entry.Extension)
			onclick_edit  += "');"
				
			printl("onclick_edit= " + onclick_edit, self)
			
			### <!-- build delete string -->
			onclick_delete = "javascript:$('#sm_save').show();window.open('/action?method=delete&what="
			onclick_delete  += str(self.type) + "&"
			
			if (self.type == 'movies'):
				onclick_delete  += "imdbid=" + str(entry.ImdbId) + "&"
			elif (self.type == 'tvshows'):
				onclick_delete  += "thetvdbid=" + str(entry.TheTvDbId) + "&"
			elif (self.type == 'tvshowepisodes'):
				onclick_delete  += "thetvdbid=" +str(entry.TheTvDbId) + "&"
			onclick_delete  += "');"
				
			printl("onclick_delete= " + onclick_delete, self)
			
			if self.type == "movies":
				tbody += u"""      <tr>
        <td><img src=\"http://val.duckbox.info/convertImg/poster/%s.png\" width="78" height="107" alt="n/a"></img></td>
        <td>%s</td>
        <td>%d</td>
        <td>%s</td>
        <td>%s</td>
        <td>
			<a href="#" onclick="%s"><img class="action_img" src="/static/img/edit-grey.png" alt="edit" title="edit" /></a>
			<a href="#" onclick="%s"><img class="action_img" src="/static/img/delete-grey.png" alt="delete" title="delete" /></a>
        </td>
      </tr>
""" % (entry.ImdbId, entry.Title, entry.Year, entry.ImdbId, entry.Filename + u"." + entry.Extension, onclick_edit, onclick_delete)
			elif self.type == "tvshows":
				tbody += u"""      <tr>
        <td><img src=\"http://val.duckbox.info/convertImg/poster/%s.png\" width="78" height="107" alt="n/a"></img></td>
        <td>%s</td>
        <td>%d</td>
        <td>%s</td>
        <td><a href=http://thetvdb.com/index.php?tab=series&id=%s target="_blank">%s</a></td>
        <td>%s</td>
		<td>
			<a href="#" onclick="%s"><img class="action_img" src="/static/img/edit-grey.png" alt="edit" title="edit" /></a>
			<a href="#" onclick="%s"><img class="action_img" src="/static/img/delete-grey.png" alt="delete" title="delete" /></a>
		</td>
      </tr>
""" % (entry.TheTvDbId, entry.Title, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.TheTvDbId, entry.Filename + u"." + entry.Extension, onclick_edit, onclick_delete)
			elif self.type == "tvshowepisodes":
				tbody += u"""      <tr>
        <td><img src=\"http://val.duckbox.info/convertImg/poster/%s.png\" width="78" height="107" alt="n/a"></img></td>
        <td>%s</td>
        <td>%d</td>
        <td>%d</td>
        <td>%d</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
		<td>
			<a href="#" onclick="%s"><img class="action_img" src="/static/img/edit-grey.png" alt="edit" title="edit" /></a>
			<a href="#" onclick="%s"><img class="action_img" src="/static/img/delete-grey.png" alt="delete" title="delete" /></a>
		</td>
      </tr>
""" % (entry.TheTvDbId, entry.Title, entry.Season, entry.Episode, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.Filename + u"." + entry.Extension, onclick_edit, onclick_delete)
			elif self.type == "failed_all":
				tbody += u"""      <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
      </tr>
""" % (entry.Path + u"/" + entry.Filename + u"." + entry.Extension, entry.CauseStr, entry.Description)
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
	
	#leads to a javascript error if ' or " is in the string
	def clean_strings(self, string):
		string = string.replace("'","")
		string = string.replace('"','')
		return string

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
