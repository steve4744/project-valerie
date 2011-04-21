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
	from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
	
	import cgi
	
	gAvailable = True
except:
	gAvailable = False

config.plugins.pvmc.plugins.webinterface = ConfigSubsection()
config.plugins.pvmc.plugins.webinterface.port = ConfigInteger(default = 8888, limits=(1, 65535) )

class Index(Resource):
	def render_GET(self, request):
		html = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Project Valerie</title>
<style type="text/css">
body { 
  color: #000000;
  background: #ffffff;
  font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
  float: none;
}

#entries
{
  margin: 0px;
  padding: 0px;
  width:100%;
  border-collapse:collapse;
}

#entries td, #entries th 
{
  font-size:1em;
  border:1px solid #98bf21;
  padding:3px 7px 2px 7px;
}

#entries th 
{
  font-size:1.1em;
  text-align:left;
  padding-top:5px;
  padding-bottom:4px;
  background-color:#A7C942;
  color:#ffffff;
}

#entries tr.alt
{
  color:#000000;
  background-color: #EAF2D3;
}

#entries tr:hover {
  background-color: #ccc;
}

#orientationbar
ul
{

  list-style-type:none;
  margin:0;
  padding:0;
  overflow:hidden;
  background-color:#A7C942;
}

div
{
  margin-bottom:20px;
}

#orientationbar
li
{
  float:left;
}

#orientationbar
a:link,a:visited
{
  display:block;
  width:120px;
  font-weight:bold;
  color:#FFFFFF;
  background-color:#98bfimport cgi21;
  text-align:center;
  padding:4px;
  text-decoration:none;
  text-transform:uppercase;
}

#orientationbar
a:hover,a:active
{
  background-color:#7A991A;
}

</style>
</head>

<body>
<div id="orientationbar">
  <ul>
    <li><a href="/vlog">Valerie Logs</a></li>
    <li><a href="/elog">Enigma2 Logs</a></li>
    <li><a href="/movies">Movies</a></li>
    <li><a href="/tvshowepisodes">TVShows</a></li>
    <li><a href="/failed_all">Failed</a></li>
  </ul>
</div>
</body>
</html>
"""
		return utf8ToLatin(html)

class Database(Resource):
	def __init__(self, type):
		self.type = type

	def render_GET(self, request):
		rows = u""
		alt = False
		manager = Manager()
		manager.start()
		if self.type == "movies":
			entries = manager.getAll(Manager.MOVIES)
		elif self.type == "tvshowepisodes":
			entries = manager.getAll(Manager.TVSHOWSEPISODES)
		elif self.type == "failed_all":
			entries = manager.getAll(Manager.FAILED_ALL)
		for entry in entries:
			if alt:
				altString = "class=\"alt\""
			else:
				altString = ""
			rows += u"""      <tr %s>
        <td>%s</td>
        <td>%d</td>
      </tr>
""" % (altString, entry.Title, entry.Year)
			alt = not alt
		html = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Project Valerie</title>

<script type="text/javascript">
function exportCSV()
{
  var url='file:///C:/cygwin/home/deshmabr/html/valerie.html';
  window.open(url, 'Download');
}

function importCSV(file)
{
  alert(file);
  location.reload(true);
}
</script>

<style type="text/css">
body { 
  color: #000000;
  background: #ffffff;
  font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
  float: none;
}

#entries
{
  margin: 0px;
  padding: 0px;
  width:100%;
  border-collapse:collapse;
}

#entries td, #entries th 
{
  font-size:1em;
  border:1px solid #98bf21;
  padding:3px 7px 2px 7px;
}

#entries th 
{
  font-size:1.1em;
  text-align:left;
  padding-top:5px;
  padding-bottom:4px;
  background-color:#A7C942;
  color:#ffffff;
}

#entries tr.alt
{
  color:#000000;
  background-color: #EAF2D3;
}

#entries tr:hover {
  background-color: #ccc;
}

#orientationbar
ul
{

  list-style-type:none;
  margin:0;
  padding:0;
  overflow:hidden;
  background-color:#A7C942;
}

div
{
  margin-bottom:20px;
}

#orientationbar
li
{
  float:left;
}

#orientationbar
a:link,a:visited
{
  display:block;
  width:120px;
  font-weight:bold;
  color:#FFFFFF;
  background-color:#98bfimport cgi21;
  text-align:center;
  padding:4px;
  text-decoration:none;
  text-transform:uppercase;
}

#orientationbar
a:hover,a:active
{
  background-color:#7A991A;
}

</style>
</head>

<body>
<div id="orientationbar">
  <ul>
    <li><a href="/vlog">Valerie Logs</a></li>
    <li><a href="/elog">Enigma2 Logs</a></li>
    <li><a href="/movies">Movies</a></li>
    <li><a href="/tvshowepisodes">TVShows</a></li>
    <li><a href="/failed_all">Failed</a></li>
  </ul>
</div>
  <table id="entries">
    <thead>
      <tr>
        <th>Name</th>
        <th>Year</th>
      </tr>
    </thead>
    <tbody>
"""
		html += rows
		html += u"""
    </tbody>
  </table>

<!--- div id="cvs">
  Export:
  <button type="button" onclick="exportCSV()">Download</button>
  <form method="post" enctype="multipart/form-data" action="/import">
    Import:
    <input type="file"></input>
    <input type="submit"></input>
  </form>
</div --->
</body>
</html>
"""
		return utf8ToLatin(html)

class Import(Resource):
	def render_POST(self, request):
		outputStream = open(filename, 'wb')
		outputStream.write(request.args['myFile'])
		outputStream.close()
		
		return """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta HTTP-EQUIV="REFRESH" content="0; url=/">
</head>
<body>
</body>
</html>
"""

def autostart(session):
	try:
		root = Resource()
		root.putChild("vlog", File('/tmp/valerie/log', defaultType="text/plain"))
		root.putChild("elog", File('/hdd/', defaultType="text/plain"))
		root.putChild("", Index())
		root.putChild("movies", Database("movies"))
		root.putChild("tvshowepisodes", Database("tvshowepisodes"))
		root.putChild("failed_all", Database("failed_all"))
		root.putChild("import", Import())
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
	registerPlugin(Plugin(name=_("WebInterface"), fnc=autostart, where=Plugin.AUTOSTART))
