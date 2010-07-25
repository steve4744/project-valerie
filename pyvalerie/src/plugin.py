# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.ProgressBar import ProgressBar
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.GUIComponent import GUIComponent
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor

from threading import Thread

import sys
import os

import Config
import DirectoryScanner
import MediaInfo
from Arts import Arts
from ImdbProvider import ImdbProvider
from TheMovieDbProvider import TheMovieDbProvider
from TheTvDbProvider import TheTvDbProvider
from Database import Database



class ProjectValerieSync(Screen):
	skin = """
		<screen position="50,50" size="620,476" title="ProjectValerieSync" >
			<eLabel text="Log:" position="10,10" size="400,20" font="Regular;18" />
			<widget name="console" position="10,30" size="400,400" font="Regular;15" />
			<eLabel text="Progress:" position="10,426" size="400,20" font="Regular;18" />
			<widget name="progress" position="10,446" size="400,20" borderWidth="1" borderColor="grey" transparent="1" />
			
			<eLabel text="" position="420,10" size="1,456" backgroundColor="grey" />
			
			<eLabel text="Last:" position="430,10" size="400,20" font="Regular;18" />
			<widget name="poster" position="430,30" size="156,214" />
			<eLabel text="Name:" position="430,260" size="180,20" font="Regular;18" />
			<widget name="name" position="440,280" size="170,20" font="Regular;16"/>
			<eLabel text="Year:" position="430,310" size="180,20" font="Regular;18" />
			<widget name="year" position="440,330" size="170,20" font="Regular;16"/>
		</screen>"""

	def __init__(self, session, args = None):
		self.skin = ProjectValerieSync.skin
		Screen.__init__(self, session)
		
		self["console"] = ScrollLabel(_("Please press OK to sync!"))
		self["progress"] = ProgressBar()
		self["poster"] = Pixmap()
		self["name"] = Label()
		self["year"] = Label()
		
		self["actions"] = ActionMap(["WizardActions"], 
		{
			"ok": self.go,
			"back": self.close,
		}, -1)
		
		self.linecount = 40
		
	def go(self):
		self["console"].lastPage()
		self.i = 0
		self.p = []
		for i in range(0, self.linecount):
			self.p.append("")
		self.thread = pyvalerie(self.output, self.progress, self.range, self.info)
		self.thread.start()
		
	def output(self, text):
		#self.p[self.i] = text
		print text
		if self.i == 0:
			self["console"].setText(text + "\n")
		else:
			self["console"].appendText(text + "\n")
			#out = ""
		#for j in range(0, self.i+1):
		#	out += self.p[j] + "\n"
		
		self.i += 1
		self.i %= self.linecount
		
		#self["console"].setText(out)
		self["console"].lastPage()
		
	def progress(self, value):
		self["progress"].setValue(value)
	
	def range(self, value):
		self["progress"].range = (0, value)
	
	def info(self, poster, name, year):
		self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + poster)
		self["name"].setText(str(name))
		self["year"].setText(str(year))
	
class pyvalerie(Thread):
	def __init__ (self, output, progress, range, info):
		Thread.__init__(self)
		self.output = output
		self.progress = progress
		self.range = range
		self.info = info
		self.output("Thread running")
		
	def run(self):
		
		#reload(sys)
		#sys.setdefaultencoding( "latin-1" )
		#sys.setdefaultencoding( "utf-8" )
		
		self.output("Loading Config")
		Config.load()
		
		self.output("Loading Database")
		db = Database()
		db.reload()
		
		self.output("Searching for media files")
		fconf = open("/hdd/valerie/paths.conf", "r")
		filetypes = fconf.readline().strip().split('|')
		self.output("Extensions: " + str(filetypes))
		print filetypes
		for path in fconf.readlines(): 
			path = path.strip()
			
			if os.path.isdir(path):
				ds = DirectoryScanner.DirectoryScanner(path)
				elementList = ds.listDirectory(filetypes, "(sample)")
		self.output("Found " + str(len(elementList)) + " media files")
		
		self.range(len(elementList))
		
		i = 0
		for element in elementList:
			self.output("(" + str(i) + "/" + str(len(elementList))  + ")")
			self.progress(i)
			i = i + 1
			
			path = element[0].replace("\\", "/").decode("latin-1")
			filename = element[1]
			extension = element[2]
			
			if "RECYCLE.BIN" in path:
				continue
				
			if db.checkDuplicate(path, element[1], element[2]):
				#self.output("Already in db [ " + element[1] + "." + element[2] + " ]")
				continue
			else:
				self.output("-> " + element[1] + "." + element[2])
				
			elementInfo = MediaInfo.MediaInfo(path, element[1], element[2])
			elementInfo.parse()
			#print elementInfo
			
			elementInfo = ImdbProvider().getMovieByTitle(elementInfo)
			
			if elementInfo.isMovie:
				# Ask TheMovieDB for the local title and plot
				elementInfo = TheMovieDbProvider().getMovieByImdbID(elementInfo)
				elementInfo = TheMovieDbProvider().getArtByImdbId(elementInfo)
				Arts().download(elementInfo)
				db.add(elementInfo)
				self.info(str(elementInfo.ImdbId) + "_poster.png", elementInfo.Title, elementInfo.Year)
			elif elementInfo.isSerie:
				elementInfo = TheTvDbProvider().getSerieByImdbID(elementInfo)
				elementInfo = TheTvDbProvider().getArtByTheTvDbId(elementInfo)
				db.add(elementInfo)
				
				elementInfoe = elementInfo.copy()
				
				elementInfoe.isSerie = False
				elementInfoe.isEpisode = True
				
				elementInfoe = TheTvDbProvider().getEpisodeByTheTvDbId(elementInfoe)
				
				db.add(elementInfoe)
				Arts().download(elementInfo)
				self.info(str(elementInfo.TheTvDbId) + "_poster.png", elementInfo.Title, elementInfo.Year)
				
			
			
		fconf.close()
		
		self.output("(" + str(i) + "/" + str(len(elementList)) + ")")
		self.progress(i)
		
		self.output("Saving database")
		db.save()
		self.output("Done")
		self.output("---------------------")
		self.output("Press Exit / Back")

def main(session, **kwargs):
	session.open(ProjectValerieSync)

def Plugins(**kwargs):
	return PluginDescriptor(name="ProjectValerieSync", description="syncs", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
	#return PluginDescriptor(name="ProjectValerieSync", description="syncs", where = PluginDescriptor.WHERE_WIZARD, fnc=main)