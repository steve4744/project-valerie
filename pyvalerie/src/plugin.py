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

from Components.MenuList import MenuList
from Components.FileList import FileList

from Components.Sources.StaticText import StaticText

from threading import Thread

import sys
import os

from sync import pyvalerie

class ProjectValerieSyncSettingsConfPathsAdd(Screen):
	skin = """
		<screen position="100,100" size="560,400" title="Add Path" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			
			<widget name="folderList" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
		</screen>"""
	
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		
		self["key_green"] = StaticText(_("Add"))
		
		self.folderList = FileList("/", showDirectories = True, showFiles = False)
		self["folderList"] = self.folderList
		self["folderList"].onSelectionChanged.append(self.selectionChanged)

		self["ProjectValerieSyncSettingsConfPathsAddActionMap"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
			"green": self.add,
			"ok": self.descent,
			"cancel": self.exit,
		}, -1)
	
	def selectionChanged(self):
		print "selectionChanged"
	
	def add(self):
		print "add"
		self.close(self.folderList.getFilename())
	
	def descent(self):
		print "descent"
		if self.folderList.canDescent():
			self.folderList.descent()
	
	def exit(self):
		print "exit"
		self.close(None)

class ProjectValerieSyncSettingsConfPaths(Screen):
	skin = """
		<screen position="100,100" size="560,400" title="Settings - Paths" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			
			<widget name="pathsList" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
		</screen>"""
	
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		
		self.pathsList = []
		fconf = open("/hdd/valerie/paths.conf", "r")
		self.filetypes = fconf.readline().strip()
		print self.filetypes
		for path in fconf.readlines(): 
			path = path.strip()
			if len(path) > 0 and path[0] != '#':
				self.pathsList.append(path)
		fconf.close()
		
		self["key_red"] = StaticText(_("Remove"))
		self["key_green"] = StaticText(_("Add"))
		#self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText(_("Save"))
		self["pathsList"] = MenuList(self.pathsList)
		
		self["ProjectValerieSyncSettingsConfPathsActionMap"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
			"cancel": self.exit,
			"red": self.remove,
			"green": self.add,
			"blue": self.save,
		}, -1)
	
	def remove(self):
		print "remove"
		entry = self["pathsList"].l.getCurrentSelection()
		print "entry: " + entry
		self.pathsList.remove(entry)
		self["pathsList"].l.setList(self.pathsList)
	
	def add(self):
		print "add"
		self.session.openWithCallback(self.addPathToList, ProjectValerieSyncSettingsConfPathsAdd)
	
	def addPathToList(self, path):
		print "addPathToList"
		if path is not None:
			print path
			if path not in self.pathsList:
				self.pathsList.append(path)
				self["pathsList"].l.setList(self.pathsList)
	
	def save(self):
		print "save"
		fconf = open("/hdd/valerie/paths.conf", "w")
		fconf.write(self.filetypes + "\n")
		for entry in self.pathsList:
			fconf.write(entry + "\n")
		fconf.close()
		
		self.exit()
	
	def ok(self):
		print "ok"
		entry = self["folderList"].l.getCurrentSelection()[1]
		print "entry: " + entry
	
	def exit(self):
		print "exit"
		self.close()
		
class ProjectValerieSyncSettings(Screen):
	skin = """
		<screen position="100,100" size="560,400" title="Settings" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget name="settingsMenu" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
		</screen>"""
		
	def __init__(self, session, args = 0):
		self.session = session
		list = []
		list.append((_("Change searchpaths"), "confPaths"))
		list.append((_("Change language"), "confLang"))
		list.append((_("Delete cache"), "clearCache"))
		list.append((_("Delete all posters/backdrops"), "delArts"))
		list.append((_("Delete database"), "delDb"))
		list.append((_("Reset filter"), "resetFl"))
		list.append((_("Exit"), "exit"))
		
		Screen.__init__(self, session)
		
		self["settingsMenu"] = MenuList(list)
		self["ProjectValerieSyncSettingsActionMap"] = ActionMap(["OkCancelActions", "DirectionActions"],
		{
			"ok": self.ok,
			"cancel": self.cancel
		}, -1)
	
	def remove(self, file):
		try:
			os.remove(temp)
		except os.error:
			pass
	
	def ok(self):
		print "ok"
		returnValue = self["settingsMenu"].l.getCurrentSelection()[1]
		print "returnValue: " + returnValue
		if returnValue is not None:
			if returnValue == "confPaths":
				self.session.open(ProjectValerieSyncSettingsConfPaths)
			elif returnValue == "clearCache":
				self.removeDir("/hdd/valerie/cache")
			elif returnValue == "delArts":
				self.removeDir("/hdd/valerie/media")
			elif returnValue == "delDb":
				self.remove("/hdd/valerie/moviedb.txt")
				self.remove("/hdd/valerie/seriesdb.txt")
				self.removeDir("/hdd/valerie/episodes")
			elif returnValue == "resetFl":
				self.remove("/hdd/valerie/pre.conf")
				self.remove("/hdd/valerie/post_movie.conf")
				self.remove("/hdd/valerie/post_tv.conf")
			elif returnValue == "exit":
				self.cancel()
	
	def cancel(self):
		print "cancel"
		self.close()
		
	def removeDir(self, dir):
		for root, dirs, files in os.walk(dir, topdown=False):
			for name in files:
				self.remove(os.path.join(root, name))
			for name in dirs:
				try:
					os.rmdir(os.path.join(root, name))
				except os.error:
					pass

class ProjectValerieSync(Screen):
	skin = """
		<screen position="50,50" size="620,476" title="ProjectValerieSync" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			
			<eLabel text="Log:" position="10,50" size="400,20" font="Regular;18" />
			<widget name="console" position="10,70" size="400,360" font="Regular;15" />
			<eLabel text="Progress:" position="10,426" size="400,20" font="Regular;18" />
			<widget name="progress" position="10,446" size="400,20" borderWidth="1" borderColor="#bbbbbb" transparent="1" />
			
			<eLabel text="" position="420,50" size="1,416" backgroundColor="#bbbbbb" />
			
			<eLabel text="Last:" position="430,50" size="400,20" font="Regular;18" />
			<widget name="poster" position="430,70" size="156,214" />
			<eLabel text="Name:" position="430,390" size="180,20" font="Regular;18" />
			<widget name="name" position="440,410" size="170,20" font="Regular;16"/>
			<eLabel text="Year:" position="430,350" size="180,20" font="Regular;18" />
			<widget name="year" position="440,370" size="170,20" font="Regular;16"/>
		</screen>"""

	def __init__(self, session, args = None):
		self.skin = ProjectValerieSync.skin
		Screen.__init__(self, session)
		
		self["key_red"] = StaticText(_("Settings"))
		
		self["console"] = ScrollLabel(_("Please press OK to sync!"))
		self["progress"] = ProgressBar()
		self["poster"] = Pixmap()
		self["name"] = Label()
		self["year"] = Label()
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"], 
		{
			"ok": self.go,
			"red": self.menu,
			"menu": self.menu,
			"cancel": self.close,
		}, -1)
		
		self.linecount = 40
		
		self.onFirstExecBegin.append(self.checkDefaults)
	
	def checkDefaults(self):
		from sync import checkDefaults as SyncCheckDefaults
		SyncCheckDefaults()
		
	
	def menu(self):
		self.session.open(ProjectValerieSyncSettings)
	
	def go(self):
		self["console"].lastPage()
		self.i = 0
		self.p = []
		for i in range(0, self.linecount):
			self.p.append("")
		self.thread = pyvalerie(self.output, self.progress, self.range, self.info)
		self.thread.start()
		
	def output(self, text):
		print text
		if self.i == 0:
			self["console"].setText(text + "\n")
		else:
			self["console"].appendText(text + "\n")
		
		self.i += 1
		self.i %= self.linecount
		self["console"].lastPage()
		
	def progress(self, value):
		self["progress"].setValue(value)
	
	def range(self, value):
		self["progress"].range = (0, value)
	
	def info(self, poster, name, year):
		print name
		self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + poster)
		self["name"].setText(name.encode("utf-8"))
		self["year"].setText(str(year))
	
def main(session, **kwargs):
	session.open(ProjectValerieSync)

def Plugins(**kwargs):
	return PluginDescriptor(name="ProjectValerieSync", description="syncs", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
	#return PluginDescriptor(name="ProjectValerieSync", description="syncs", where = PluginDescriptor.WHERE_WIZARD, fnc=main)
