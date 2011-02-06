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
from enigma import getDesktop
from Components.MenuList import MenuList
from Components.FileList import FileList

from Components.Sources.StaticText import StaticText

from threading import Thread

import sys
import os

from sync import pyvalerie

from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ
import gettext
from Components.Language import language

def localeInit():
	lang = language.getLanguage()
	environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ProjectValerie", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ProjectValerie/locale/"))

def _(txt):
	t = gettext.dgettext("ProjectValerie", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)

class ProjectValerieSyncSettingsConfPathsAdd(Screen):
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1280.png"/>
            <widget source="Title" render="Label" zPosition="5" halign="center" position="60,60" size="1160,50" font="Modern;35" backgroundColor="#FF000000" foregroundColor="#006CA4C5" transparent="1"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" position="60,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" position="280,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="500,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_blue.png" position="870,660" size="15,16" alphatest="blend"/>
            <widget source="key_green" render="Label" position="300,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="folderList" position="60,140" size="1160,470" scrollbarMode="showOnDemand" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1" enableWrapAround="1"/>
            </screen>"""
        elif sz_w == 1024:
            skin = """
            <screen position="center,center" size="560,400" title=" " flags="wfNoBorder">
                <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>			
                <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
                <widget name="folderList" position="10,50" size="550,340" scrollbarMode="showOnDemand"/>
            </screen>"""
        else:
            skin = """
            <screen position="center,center" size="560,400" title=" ">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>			
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget name="folderList" position="10,50" size="550,340" scrollbarMode="showOnDemand" enableWrapAround="1"/>
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
                self.onLayoutFinish.append(self.setCustomTitle)
                
        def setCustomTitle(self):
                self.setTitle(_("Add Path"))
	
	def selectionChanged(self):
		print "selectionChanged"
	
	selection = ""
	
	def add(self):
		print "add"
		print "prev", self.selection
		print "now", self.folderList.getFilename()
		if self.selection in self.folderList.getFilename():
			self.close(self.folderList.getFilename())
		else:
			self.close(self.selection)
	
	def descent(self):
		print "descent"
		if self.folderList.canDescent():
			self.selection = self.folderList.getFilename()
			self.folderList.descent()
	
	def exit(self):
		print "exit"
		self.close(None)

class ProjectValerieSyncSettingsConfPaths(Screen):
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1280.png"/>
            <widget source="Title" render="Label" zPosition="5" halign="center" position="60,60" size="1160,50" font="Modern;35" backgroundColor="#FF000000" foregroundColor="#006CA4C5" transparent="1"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" position="60,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" position="280,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="500,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_blue.png" position="870,660" size="15,16" alphatest="blend"/>
            <widget source="key_red" render="Label" position="80,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="key_green" render="Label" position="300,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="key_yellow" render="Label" position="520,655" zPosition="1" size="350,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="key_blue" render="Label" position="890,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="pathsList" position="60,140" size="1160,440" scrollbarMode="showOnDemand" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1" enableWrapAround="1"/>
            </screen>"""
        elif sz_w == 1024:
            skin = """
            <screen position="center,center" size="560,400" title=" " flags="wfNoBorder">
                <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
                <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
                <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
                <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
                <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>
                <widget name="pathsList" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
            </screen>"""
        else:
            skin = """
            <screen position="center,center" size="560,400" title=" ">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>
            <widget name="pathsList" position="10,50" size="550,340" scrollbarMode="showOnDemand" enableWrapAround="1"/>
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
			p = path.split('|')
			path = p[0]
			if len(p) > 1:
				type = p[1]
			else:
				type = "MOVIE_AND_TV"
			
			if len(path) > 0 and path[0] != '#':
				self.pathsList.append((path + " [" + type + "]", path, type))
		fconf.close()
		
		self["key_red"] = StaticText(_("Remove"))
		self["key_green"] = StaticText(_("Add"))
		self["key_yellow"] = StaticText(_("Toggle Type"))
		self["key_blue"] = StaticText(_("Save"))
		self["pathsList"] = MenuList(self.pathsList)
		
		self["ProjectValerieSyncSettingsConfPathsActionMap"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
			"cancel": self.exit,
			"red": self.remove,
			"green": self.add,
			"yellow": self.toggleType,
			"blue": self.save,
		}, -1)
                self.onLayoutFinish.append(self.setCustomTitle)
                
        def setCustomTitle(self):
                self.setTitle(_("Synchronize Manager Searchpaths"))
	
	def remove(self):
		print "remove"
		entry = self["pathsList"].l.getCurrentSelection()
		print "entry: ", entry
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
				type = "MOVIE_AND_TV"
				self.pathsList.append((path + " [" + type + "]", path, type))
				self["pathsList"].l.setList(self.pathsList)
	
	def toggleType(self):
		entry = self["pathsList"].l.getCurrentSelection()
		print "entrySrc: ", entry
		index = self.pathsList.index(entry)
		print "index: ", index
		#self.pathsList.remove(entry)
		if entry[2] == "MOVIE_AND_TV":
			entry = (entry[1] + " [MOVIE]", entry[1], "MOVIE")
		elif entry[2] == "MOVIE":
			entry = (entry[1] + " [TV]", entry[1], "TV")
		elif entry[2] == "TV":
			entry = (entry[1] + " [MOVIE_AND_TV]", entry[1], "MOVIE_AND_TV")
		print "entryDst: ", entry
		self.pathsList[index] = entry
		self["pathsList"].l.setList(self.pathsList)
		
	def save(self):
		print "save"
		fconf = open("/hdd/valerie/paths.conf", "w")
		fconf.write(self.filetypes + "\n")
		for entry in self.pathsList:
			fconf.write(entry[1] + "|" + entry[2] + "\n")
		fconf.close()
		
		self.exit()
	
	def ok(self):
		print "ok"
		entry = self["folderList"].l.getCurrentSelection()[1]
		print "entry: " + entry
	
	def exit(self):
		print "exit"
		self.close()

from Components.ConfigList import ConfigListScreen
from Components.config import ConfigSelection
from Components.config import ConfigYesNo
from Components.config import *

class ProjectValerieSyncSettingsConfSettings(Screen, ConfigListScreen):
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1280.png"/>
            <widget source="Title" render="Label" zPosition="5" halign="center" position="60,60" size="1160,50" font="Modern;35" backgroundColor="#FF000000" foregroundColor="#006CA4C5" transparent="1"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" position="60,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" position="280,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="500,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_blue.png" position="870,660" size="15,16" alphatest="blend"/>
            <widget source="key_red" render="Label" position="80,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="key_green" render="Label" position="300,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <!-- widget source="key_yellow" render="Label" position="520,655" zPosition="1" size="350,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/ -->
            <!-- widget source="key_blue" render="Label" position="890,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/ -->
            <widget name="config" position="60,140" size="1160,340" scrollbarMode="showOnDemand" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1" enableWrapAround="1"/>
            </screen>"""
        elif sz_w == 1024:
            skin = """
            <screen position="center,center" size="660,400" title=" " flags="wfNoBorder">
                <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
                <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
                <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
                <!-- widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/ -->
                <!-- widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/ -->
                <widget name="config" position="10,50" size="650,340" scrollbarMode="showOnDemand" />
            </screen>"""
        else:
            skin = """
            <screen position="center,center" size="660,400" title=" ">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <!-- widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/ -->
            <!-- widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/ -->
            <widget name="config" position="10,50" size="650,340" scrollbarMode="showOnDemand" enableWrapAround="1"/>
            </screen>"""

	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))

		ConfigListScreen.__init__(self, [])
		self.initConfigList()
		#config.mediaplayer.saveDirOnExit.addNotifier(self.initConfigList)


		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
		    "green": self.save,
		    "red": self.cancel,
		    "cancel": self.cancel,
		    "ok": self.ok,
		}, -2)
                self.onLayoutFinish.append(self.setCustomTitle)
                
        def setCustomTitle(self):
                self.setTitle(_("Synchronize settings"))

	def initConfigList(self, element=None):
		print "[initConfigList]", element
		self.list = []
		try:
			defaultLang = "en"
			defaultDelete = False
			fconf = open("/hdd/valerie/valerie.conf", "r")
			for path in fconf.readlines(): 
				path = path.strip()
				p = path.split('=')
				key = p[0]
				if len(p) > 1:
					value = p[1]
				if key == "local":
					defaultLang = value
				elif key == "delete":
					if value == "true":
						defaultDelete = True
			fconf.close()
			
			
			self.local = ConfigSelection(default=defaultLang, choices = ["en", "de", "it", "es", "fr", "pt"])
			self.list.append(getConfigListEntry(_("Language"), self.local))
			
			self.deleteIfNotFound = ConfigYesNo(default = defaultDelete)
			self.list.append(getConfigListEntry(_("Delete movies if file can not be found"), self.deleteIfNotFound))
			
		except KeyError:
			print "keyError"

		

		self["config"].setList(self.list)	

	def changedConfigList(self):
		self.initConfigList()

	def ok(self):
		print "ok"

	def save(self):
		print "save"
		print self.local.value
		print self.deleteIfNotFound.value
		
		conf = []
		fconf = open("/hdd/valerie/valerie.conf", "r")
		for path in fconf.readlines(): 
			path = path.strip()
			p = path.split('=')
			key = p[0]
			if key is not None and key != "local" and key != "delete":
				conf.append(path)
		fconf.close()
		
		fconf = open("/hdd/valerie/valerie.conf", "w")
		for entry in conf:
			fconf.write(entry + "\n")
		fconf.write("local=" + self.local.value + "\n")
		fconf.write("delete=" + str(self.deleteIfNotFound.value).lower() + "\n")
		fconf.close()
		self.close()

	def cancel(self):
		self.close()

class ProjectValerieSyncSettings(Screen):
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1280.png"/>
            <widget source="Title" render="Label" zPosition="5" halign="center" position="60,60" size="1160,50" font="Modern;35" backgroundColor="#FF000000" foregroundColor="#006CA4C5" transparent="1"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" position="60,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" position="280,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="500,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_blue.png" position="870,660" size="15,16" alphatest="blend"/>
            <widget name="settingsMenu" position="60,140" size="1160,340" scrollbarMode="showOnDemand" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1" enableWrapAround="1"/>
            </screen>"""
        elif sz_w == 1024:
            skin = """
            <screen position="center,center" size="560,400" title=" " flags="wfNoBorder">
                <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
                <widget name="settingsMenu" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
            </screen>"""
        else:
            skin = """
            <screen position="center,center" size="560,400" title=" ">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
            <widget name="settingsMenu" position="10,50" size="550,340" scrollbarMode="showOnDemand" enableWrapAround="1"/>
            </screen>"""

	def __init__(self, session, args = 0):
		self.session = session
		list = []
		list.append((_("Change searchpaths"), "confPaths"))
		list.append((_("Change settings"), "confSettings"))
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
                self.onLayoutFinish.append(self.setCustomTitle)
                
        def setCustomTitle(self):
                self.setTitle(_("Synchronize Manager options"))
	
	def remove(self, file):
		try:
			os.remove(file)
		except os.error:
			pass
	
	def ok(self):
		print "ok"
		returnValue = self["settingsMenu"].l.getCurrentSelection()[1]
		print "returnValue: " + returnValue
		if returnValue is not None:
			if returnValue == "confPaths":
				self.session.open(ProjectValerieSyncSettingsConfPaths)
			elif returnValue == "confSettings":
				self.session.open(ProjectValerieSyncSettingsConfSettings, self)
			elif returnValue == "clearCache":
				self.removeDir("/hdd/valerie/cache")
			elif returnValue == "delArts":
				self.removeDir("/hdd/valerie/media")
			elif returnValue == "delDb":
				self.remove("/hdd/valerie/moviedb.txt")
				self.remove("/hdd/valerie/movies.txd")
				self.remove("/hdd/valerie/movies.db")
				self.remove("/hdd/valerie/seriesdb.txt")
				self.remove("/hdd/valerie/tvshows.txd")
				self.remove("/hdd/valerie/tvshows.db")
				self.removeDir("/hdd/valerie/episodes")
				self.remove("/hdd/valerie/episodes.db")
				self.remove("/hdd/valerie/fastcrawl.bin")
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

class ProjectValerieSyncInfo():
	outputInstance = None
	syncInfo = None
	i = 0
	linecount = 40
	progress = 0
	range = 0
	lines = []
	
	poster = None
	name = ""
	year = 0
	
	inForeground = False
	inProgress = False
	
	session = None
	
	def reset(self):
		self.i = 0
		self.linecount = 40
		self.progress = 0
		self.range = 0
		self.lines = []
		
		self.poster = None
		self.name = ""
		self.year = 0

gSyncInfo = None

class ProjectValerieSyncFinished(Screen):
	skin = """
		<screen position="center,0" size="300,100" title=" " >
			<widget name="info" position="10,10" size="280,80" font="Regular;30" halign="center" valign="center" />
		</screen>"""
		
	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		
		self["info"] = Label(_("Synchronize finished"))
		
		self["ProjectValerieSyncFinishedActionMap"] = ActionMap(["OkCancelActions", "DirectionActions"],
		{
			"ok": self.close,
			"cancel": self.close
		}, -1)
                self.onLayoutFinish.append(self.setCustomTitle)
                
        def setCustomTitle(self):
                self.setTitle(_("Synchronize Manager"))
		
from MediaInfo import MediaInfo
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Components.Sources.List import List
from Manager import Manager
from Components.Input import Input
import Utf8

class ProjectValerieSyncManagerInfo(Screen):
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1280.png"/>
            <widget source="Title" render="Label" zPosition="5" halign="center" position="60,60" size="1160,50" font="Modern;35" backgroundColor="#FF000000" foregroundColor="#006CA4C5" transparent="1"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" position="60,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" position="280,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="500,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_blue.png" position="870,660" size="15,16" alphatest="blend"/>
            <widget source="key_red" render="Label" position="80,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="key_green" render="Label" position="300,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="key_yellow" render="Label" position="520,655" zPosition="1" size="350,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="key_blue" render="Label" position="890,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="pathtxt" render="Label"  position="60,140" size="150,30" font="Regular;22" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="filenametxt" render="Label" position="60,170" size="150,30" font="Regular;22" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="titletxt" render="Label" position="60,200" size="150,30" font="Regular;22" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="yeartxt" render="Label" position="60,230" size="150,30" font="Regular;22" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="seasontxt" render="Label" position="60,260" size="150,30" font="Regular;22" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="episodetxt" render="Label" position="60,290" size="150,30" font="Regular;22" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="path" position="210,140" size="1010,50" font="Regular;22" halign="left" valign="top" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="filename" position="210,170" size="1010,50" font="Regular;22" halign="left" valign="top" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="title" position="210,200" size="1010,50" font="Regular;22" halign="left" valign="top" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="year" position="210,230" size="1010,25" font="Regular;22" halign="left" valign="top" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="season" position="210,260" size="1010,25" font="Regular;22" halign="left" valign="top" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="episode" position="210,290" size="1010,25" font="Regular;22" halign="left" valign="top" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            </screen>"""
        elif sz_w == 1024:
            skin = """
            <screen position="center,center" size="620,476" title=" " flags="wfNoBorder">
                <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
                <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
                <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
                <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
                <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>
                <widget source="pathtxt" render="Label"  position="10,50" size="150,25" font="Regular;20"/>
                <widget source="filenametxt" render="Label"  position="10,100" size="150,25" font="Regular;20"/>
                <widget source="titletxt" render="Label"  position="10,150" size="150,25" font="Regular;20"/>
                <widget source="yeartxt" render="Label"  position="10,200" size="150,25" font="Regular;20"/>
                <widget source="seasontxt" render="Label"  position="10,230" size="150,25" font="Regular;20"/>
                <widget source="episodetxt" render="Label"  position="10,260" size="150,25" font="Regular;20"/>
                <widget name="path" position="160,50" size="450,50" font="Regular;20" halign="left" valign="top"/>
                <widget name="filename" position="160,100" size="450,50" font="Regular;20" halign="left" valign="top"/>
                <widget name="title" position="160,150" size="450,50" font="Regular;20" halign="left" valign="top"/>
                <widget name="year"  position="160,200"  size="450,25" font="Regular;20" halign="left" valign="top"/>
                <widget name="season"  position="160,230"  size="450,25" font="Regular;20" halign="left" valign="top"/>
                v<widget name="episode"  position="160,260"  size="450,25" font="Regular;20" halign="left" valign="top"/>
            </screen>"""
        else:
            skin = """
            <screen position="center,center" size="620,476" title=" ">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>
            <widget source="pathtxt" render="Label" position="10,50" size="150,25" font="Regular;20"/>
            <widget source="filenametxt" render="Label" position="10,100" size="150,25" font="Regular;20"/>
            <widget source="titletxt" render="Label" position="10,150" size="150,25" font="Regular;20"/>
            <widget source="yeartxt" render="Label" position="10,200" size="150,25" font="Regular;20"/>
            <widget source="seasontxt" render="Label" position="10,230" size="150,25" font="Regular;20"/>
            <widget source="episodetxt" render="Label" position="10,260" size="150,25" font="Regular;20"/>
            <widget name="path" position="160,50" size="450,50" font="Regular;20" halign="left" valign="top"/>
            <widget name="filename" position="160,100" size="450,50" font="Regular;20" halign="left" valign="top"/>
            <widget name="title" position="160,150" size="450,50" font="Regular;20" halign="left" valign="top"/>
            <widget name="year" position="160,200" size="450,25" font="Regular;20" halign="left" valign="top"/>
            <widget name="season" position="160,230" size="450,25" font="Regular;20" halign="left" valign="top"/>
            <widget name="episode" position="160,260" size="450,25" font="Regular;20" halign="left" valign="top"/>
            </screen>"""

	def __init__(self, session, manager, element):
		Screen.__init__(self, session)
		
		self.manager = manager
		self.element = element
		self.elementParent = None
		
		self["key_red"] = StaticText(_("Alternatives"))
		self["key_green"] = StaticText(_("IMDb ID"))
		self["key_yellow"] = StaticText(_(" "))
		self["key_blue"] = StaticText(_("Save"))

		self["pathtxt"] = StaticText(_("Path:"))
		self["filenametxt"] = StaticText(_("Filename:"))
		self["titletxt"] = StaticText(_("Title:"))
		self["yeartxt"] = StaticText(_("Year:"))
		self["seasontxt"] = StaticText(_("Season:"))
		self["episodetxt"] = StaticText(_("Episode:"))

		self["path"] = Label()
		self["filename"] = Label()				
		self["title"] =  Label()
		self["year"] =  Label()
		self["season"] =  Label()
		self["episode"] =  Label()
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"], 
		{
			"red": self.showAlternatives,
			"green": self.showEnterImdbId,
			"blue": self.save,
			"cancel": self.close,
			"ok": self.close,
		}, -1)
                self.onLayoutFinish.append(self.setCustomTitle)
                self.onFirstExecBegin.append(self.onLoad)
                
        def setCustomTitle(self):
                self.setTitle(_("Synchronize Manager Info"))
	
	def onLoad(self):
		
		self["path"].setText(Utf8.utf8ToLatin(self.element.Path))
		self["filename"].setText(Utf8.utf8ToLatin(self.element.Filename) + "." + Utf8.utf8ToLatin(self.element.Extension))
		if type(self.element) is MediaInfo:	
			self["title"].setText(Utf8.utf8ToLatin(self.element.Title))
			self["year"].setText(str(self.element.Year))
			if self.element.isMovie:
				self["season"].setText(" ")
				self["episode"].setText(" ")
			else:
				self["season"].setText(str(self.element.Season))
				self["episode"].setText(str(self.element.Episode))
		else:
			self["title"].setText(" ")
			self["year"].setText(" ")
			self["season"].setText(" ")
			self["episode"].setText(" ")
			
		
	def close(self):
		Screen.close(self, None)
		
	def showEnterImdbId(self):
		self.session.openWithCallback(self.showEnterImdbIdCallback, InputBox, _(title="IMDb ID without tt"), type=Input.NUMBER)#useableChars="0123456789")
	
	def showEnterImdbIdCallback(self, what):
		print "showEnterImdbIdCallback", what
		if what is not None:
			element = self.manager.syncElement(self.element.Path, self.element.Filename, self.element.Extension, "tt" + what, False)
			if element is not None:
				if len(element) == 2:
					self.elementParent = element[0]
					self.element = element[1]
				else:
					self.element = element[0]
				self.onLoad()
	
	def showAlternatives(self):
		results = self.manager.searchAlternatives(self.element)
		
		if results is None:
			 self.session.open(MessageBox, _("No alternatives found"), type = MessageBox.TYPE_INFO)
		else:
			menu = []
			for result in results:
				#if result.ImdbId != self.element.ImdbId:
				tvFlag = ""
				if result.IsTVSeries is True:
					tvFlag = "(TV) "
				menu.append(("[" + str(result.Year) + "] " + tvFlag + Utf8.utf8ToLatin(result.Title), result.ImdbId, result.IsTVSeries))

			self.session.openWithCallback(self.showAlternativesCallback, ChoiceBox, title=_("Alternatives"), list=menu)

	def showAlternativesCallback(self, what):
		print "showAlternativesCallback", what
		if what is not None and len(what) == 3:
			element = self.manager.syncElement(self.element.Path, self.element.Filename, self.element.Extension, what[1], what[2])
			if element is not None:
				if len(element) == 2:
					self.elementParent = element[0]
					self.element = element[1]
				else:
					self.element = element[0]
				self.onLoad()
		
	def save(self):
		if self.elementParent is not None:
			Screen.close(self, (self.elementParent, self.element, ))
		else:
			Screen.close(self, (self.element, ))
		

class ProjectValerieSyncManager(Screen):
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1280.png"/>
            <widget source="Title" render="Label" transparent="1" zPosition="5" halign="center" position="60,60" size="1160,50" font="Modern;35" backgroundColor="#FF000000" foregroundColor="#006CA4C5"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" position="60,660" size="15,16" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" position="280,660" size="15,16" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="500,660" size="15,16" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/button_blue.png" position="870,660" size="15,16" alphatest="on"/>
            <widget source="key_red" render="Label" position="80,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" transparent="1"/>
            <widget source="key_green" render="Label" position="300,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" transparent="1"/>
            <widget source="key_yellow" render="Label" position="520,655" zPosition="1" size="350,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" transparent="1"/>
            <widget source="key_blue" render="Label" position="890,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" transparent="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/buttons/key_ok.png" position="1185,655" size="35,25" zPosition="2" alphatest="blend"/>
            <widget source="listview" render="Listbox" zPosition="2" position="60,140" size="1160,455" scrollbarMode="showOnDemand" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1" enableWrapAround="1">
                <convert type="TemplatedMultiContent">
                    {"template": [  MultiContentEntryText(pos = (10, 0),  size = (1120, 35), font=0, flags = RT_HALIGN_LEFT,  text = 0),
                                MultiContentEntryText(pos = (0, 30), size = (1120, 30), font=1, flags = RT_HALIGN_RIGHT, text = 1) ],
                    "fonts": [gFont("Modern", 25), gFont("Modern", 20)],
                    "itemHeight": 65
                    }
                </convert>
            </widget>
        </screen>"""
        elif sz_w == 1024:
            skin = """
            <screen position="center,center" size="620,476" title=" " flags="wfNoBorder">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>
            <widget source="listview" render="Listbox" zPosition="2" position="10,50" size="600,390" scrollbarMode="showOnDemand" >
                <convert type="TemplatedMultiContent">
                    {"template": [  MultiContentEntryText(pos = (0, 0),  size = (570, 30), font=0, flags = RT_HALIGN_LEFT,  text = 0),
                                MultiContentEntryText(pos = (0, 30), size = (570, 25), font=1, flags = RT_HALIGN_RIGHT, text = 1) ],
                    "fonts": [gFont("Modern", 25), gFont("Modern", 20)],
                    "itemHeight": 65
                    }
                </convert>
            </widget>
        </screen>"""
        else:
            skin = """
            <screen position="center,center" size="620,476" title=" ">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>
            <widget source="listview" render="Listbox" zPosition="2" position="10,50" size="600,390" scrollbarMode="showOnDemand" >
                <convert type="TemplatedMultiContent">
                    {"template": [  MultiContentEntryText(pos = (0, 0),  size = (570, 30), font=0, flags = RT_HALIGN_LEFT,  text = 0),
                                MultiContentEntryText(pos = (0, 30), size = (570, 25), font=1, flags = RT_HALIGN_RIGHT, text = 1) ],
                    "fonts": [gFont("Modern", 25), gFont("Modern", 20)],
                    "itemHeight": 65
                    }
                </convert>
            </widget>
        </screen>"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		
		list = []
		self["listview"] = List(list, True)
		self["key_red"] = StaticText(_("Failed"))
		self["key_green"] = StaticText(_("Movies"))
		self["key_yellow"] = StaticText(_("Series"))
		self["key_blue"] = StaticText(_(" "))
		
		self.manager = Manager()
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"], 
		{
			"red": self.loadFailed,
			"green": self.loadMovies,
			"yellow": self.loadTVShows,
			"cancel": self.onFinish,
			"ok": self.showInfo,
		}, -1)
                self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.onLoad)

        def setCustomTitle(self):
                self.setTitle(_("Synchronize Manager Overview"))
	
	def onLoad(self):
		self.manager.start()
		self.loadFailed()
	
	def onFinish(self):
		self.manager.finish()
		Screen.close(self)
	
	def loadFailed(self):
		self.load(Manager.FAILED)
		
	def loadMovies(self):
		self.load(Manager.MOVIES)
	
	def loadTVShows(self):
		self.load(Manager.TVSHOWS)
	
	def load(self, type):
		self.currentCategory = type
		list = []
		entries = self.manager.getAll(type)
		if type == Manager.FAILED:
			for entry in entries:
				list.append((Utf8.utf8ToLatin(entry.Filename) + "." + Utf8.utf8ToLatin(entry.Extension), 
							Utf8.utf8ToLatin(entry.CauseStr), entry), )
		else:
			for entry in entries:
				list.append((Utf8.utf8ToLatin(entry.Filename) + "." + Utf8.utf8ToLatin(entry.Extension), 
							Utf8.utf8ToLatin(entry.Title), entry), )

		self["listview"].setList(list)
	
	def showInfo(self):
		selection = self["listview"].getCurrent()
		if selection is not None:
			self.oldElement = selection[2]
			self.session.openWithCallback(self.elementChanged, ProjectValerieSyncManagerInfo, self.manager, self.oldElement)
			
	def elementChanged(self, newElement):
		print "elementChanged", newElement
		if newElement is not None:
			if len(newElement) == 2:
				testElement = newElement[1]
			else:
				testElement = newElement[0]
			if testElement is not self.oldElement:
				print "elementChanged - Changed"
				self.manager.replace(self.oldElement, newElement)
				index = self["listview"].getIndex()
				self.load(self.currentCategory)
				if index >= self["listview"].count():
					index = self["listview"].count() - 1
				self["listview"].setIndex(index)
					
	
class ProjectValerieSync(Screen):
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1280.png"/>
            <widget source="Title" render="Label" transparent="1" zPosition="5" halign="center" position="60,60" size="1160,50" font="Modern;35" backgroundColor="#FF000000" foregroundColor="#006CA4C5"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" position="60,660" size="15,16" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" position="280,660" size="15,16" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="500,660" size="15,16" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/button_blue.png" position="870,660" size="15,16" alphatest="on"/>
            <widget source="key_red" render="Label" position="80,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" transparent="1"/>
            <widget source="key_green" render="Label" position="300,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" transparent="1"/>
            <widget source="key_yellow" render="Label" position="520,655" zPosition="1" size="350,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" transparent="1"/>
            <widget source="key_blue" render="Label" position="890,655" zPosition="1" size="200,28" font="Regular;20" halign="left" valign="center" backgroundColor="#FF000000" transparent="1"/>
            <widget source="logtxt" render="Label" position="60,140" size="874,28" font="Modern;20" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="console" position="60,175" size="874,390" font="Regular;20" transparent="1" foregroundColor="#ffffff"/>
            <widget source="progresstxt" render="Label" position="60,600" size="400,28" font="Modern;20" transparent="1" foregroundColor="#ffffff"/>
            <widget name="progress" position="190,610" size="1030,12" borderWidth="1" borderColor="#bbbbbb" transparent="1"/>
            <eLabel position="954,140" size="2,415" backgroundColor="#ffffff"/>
            <widget source="lasttxt" render="Label" position="964,140" size="256,28" font="Modern;20" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="poster" position="964,175" size="156,214"/>
            <widget source="yeartxt" render="Label" position="964,400" size="256,28" font="Modern;20" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="year" position="964,425" size="256,28" font="Modern;20" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget source="nametxt" render="Label" position="964,450" size="256,28" font="Modern;20" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            <widget name="name" position="964,475" size="256,70" font="Modern;20" backgroundColor="#FF000000" foregroundColor="#ffffff" transparent="1"/>
            </screen>"""
        elif sz_w == 1024:
            skin = """
            <screen position="center,center" size="620,476" title=" " flags="wfNoBorder">
                <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
                <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
                <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
                <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
                <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
                <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>
                <widget source="logtxt" render="Label" position="10,50" size="400,20" font="Regular;18"/>
                <widget name="console" position="10,70" size="400,360" font="Regular;15"/>
                <widget source="progresstxt" render="Label" position="10,426" size="400,20" font="Regular;18"/>
                <widget name="progress" position="10,446" size="400,20" borderWidth="1" borderColor="#bbbbbb" transparent="1"/>
                <eLabel text="" position="420,50" size="1,416" backgroundColor="#bbbbbb"/>
                <widget source="lasttxt" render="Label" position="430,50" size="400,20" font="Regular;18"/>
                <widget name="poster" position="430,70" size="156,214"/>
                <widget source="yeartxt" render="Label" position="430,350" size="180,20" font="Regular;18"/>
                <widget name="year" position="440,370" size="170,20" font="Regular;16"/>
                <widget source="nametxt" render="Label" position="430,390" size="180,20" font="Regular;18"/>
                <widget name="name" position="440,410" size="170,60" font="Regular;16"/>
            </screen>"""
        else:
            skin = """
            <screen position="center,center" size="620,476" title=" " >
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on"/>
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on"/>
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;16" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
            <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>
            <widget source="logtxt" render="Label" position="10,50" size="400,20" font="Regular;18"/>
            <widget name="console" position="10,70" size="400,360" font="Regular;15"/>
            <widget source="progresstxt" render="Label" position="10,426" size="400,20" font="Regular;18"/>
            <widget name="progress" position="10,446" size="400,20" borderWidth="1" borderColor="#bbbbbb" transparent="1"/>
            <eLabel text="" position="420,50" size="1,416" backgroundColor="#bbbbbb"/>
            <widget source="lasttxt" render="Label" position="430,50" size="400,20" font="Regular;18"/>
            <widget name="poster" position="430,70" size="156,214"/>
            <widget source="yeartxt" render="Label" position="430,350" size="180,20" font="Regular;18"/>
            <widget name="year" position="440,370" size="170,20" font="Regular;16"/>
            <widget source="nametxt" render="Label" position="430,390" size="180,20" font="Regular;18"/>
            <widget name="name" position="440,410" size="170,60" font="Regular;16"/>
            </screen>"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		
		self["key_red"] = StaticText(_("Manage"))
		self["key_green"] = StaticText(_("Synchronize"))
		self["key_yellow"] = StaticText(_("Fast Synchronize"))
		self["key_blue"] = StaticText(_("Settings"))
		
		self["console"] = ScrollLabel(_("Please press the green button to start synchronize!\n"))
		self["progress"] = ProgressBar()
		self["poster"] = Pixmap()
		self["name"] = Label()
		self["year"] = Label()
                
                self["logtxt"] = StaticText(_("Log:"))
		self["progresstxt"] = StaticText(_("Progress:"))
		self["lasttxt"] = StaticText(_("Last:"))
		self["yeartxt"] = StaticText(_("Year:"))
                self["nametxt"] = StaticText(_("Name:"))
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"], 
		{
			"green": self.go,
			"yellow": self.gofast,
			"red": self.manage,
			"blue": self.menu,
			"menu": self.menu,
			"cancel": self.close,
		}, -1)
                self.onLayoutFinish.append(self.setCustomTitle)
		
        def setCustomTitle(self):
                self.setTitle(_("Synchronize Manager"))		
		
		print "PYTHONPATH=", sys.path
		from Tools.Directories import resolveFilename, SCOPE_PLUGINS 
		sys.path.append(resolveFilename(SCOPE_PLUGINS, "Extensions/ProjectValerieSync") )

		self.onFirstExecBegin.append(self.startup)
	
	def startup(self):
		global gSyncInfo
		print "startup", type(gSyncInfo)
		if gSyncInfo is None:
			gSyncInfo = ProjectValerieSyncInfo()
		gSyncInfo.outputInstance = self
		gSyncInfo.session = self.session
		print "gSyncInfo.inProgress", gSyncInfo.inProgress
		if gSyncInfo.inProgress is True:
			gSyncInfo.inForeground = True
			
			self.range(gSyncInfo.range)
			self.progress(gSyncInfo.progress)
			self.info(gSyncInfo.poster, gSyncInfo.name, gSyncInfo.year)
			
			self["console"].setText("")
			
			if len(gSyncInfo.lines) > 0:
				for line in gSyncInfo.lines:
					self["console"].appendText(line + "\n")
				self["console"].lastPage()
		else:	
			self.checkDefaults()
	
	def checkDefaults(self):
		from sync import checkDefaults as SyncCheckDefaults
		SyncCheckDefaults()

	def close(self):
		global gSyncInfo
		gSyncInfo.inForeground = False
		Screen.close(self)
	
	def menu(self):
		if gSyncInfo.inProgress is False:
			self.session.open(ProjectValerieSyncSettings)
	
	def manage(self):
		if gSyncInfo.inProgress is False:
			self.session.open(ProjectValerieSyncManager)
	
	def go(self):
		if gSyncInfo.inProgress is False:
			self["console"].lastPage()
			global gSyncInfo
			gSyncInfo.reset()
			gSyncInfo.inForeground = True
			gSyncInfo.inProgress = True
			gSyncInfo.outputInstance["console"].setText("")
			self.thread = pyvalerie(self.output, self.progress, self.range, self.info, self.finished, pyvalerie.NORMAL)
			self.thread.start()
	
	def gofast(self):
		if gSyncInfo.inProgress is False:
			self["console"].lastPage()
			global gSyncInfo
			gSyncInfo.reset()
			gSyncInfo.inForeground = True
			gSyncInfo.inProgress = True
			gSyncInfo.outputInstance["console"].setText("")
			self.thread = pyvalerie(self.output, self.progress, self.range, self.info, self.finished, pyvalerie.FAST)
			self.thread.start()
	
	def finished(self, successfully):
		gSyncInfo.inProgress = False
		if gSyncInfo.inForeground is False:
			gSyncInfo.session.open(ProjectValerieSyncFinished)
		
	def output(self, text):
		global gSyncInfo
		print text
		print "gSyncInfo.inProgress", gSyncInfo.inProgress
		print "gSyncInfo.inForeground", gSyncInfo.inForeground
		if gSyncInfo.inForeground is True:
			if len(gSyncInfo.lines) >= gSyncInfo.linecount:
				gSyncInfo.i = 0
				gSyncInfo.outputInstance["console"].setText("")
			gSyncInfo.outputInstance["console"].appendText(text + "\n")

			gSyncInfo.i += 1
			
			gSyncInfo.outputInstance["console"].lastPage()
		else:
			gSyncInfo.i = 0
			
		if len(gSyncInfo.lines) >= gSyncInfo.linecount:
			del gSyncInfo.lines[:]
		gSyncInfo.lines.append(text)
			
		
	def progress(self, value):
		gSyncInfo.progress = value
		if gSyncInfo.inForeground is True:
			gSyncInfo.outputInstance["progress"].setValue(value)
	
	def range(self, value):
		gSyncInfo.range = value
		if gSyncInfo.inForeground is True:
			gSyncInfo.outputInstance["progress"].range = (0, value)
	
	def info(self, poster, name, year):
		print name
		gSyncInfo.poster = poster
		gSyncInfo.str = str
		gSyncInfo.year = year
		
		if gSyncInfo.inForeground is True:
			try:
				if poster is not None and len(poster) > 0:
					gSyncInfo.outputInstance["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + poster)
				if name is not None and len(name) > 0:
					gSyncInfo.outputInstance["name"].setText(name)
				if year is not None and year > 0:
					gSyncInfo.outputInstance["year"].setText(str(year))
			except Exception, ex:
				print "ProjectValerieSync::info", ex
	
def main(session, **kwargs):
	session.open(ProjectValerieSync)

def Plugins(**kwargs):
	return PluginDescriptor(name="ProjectValerieSync", description="syncs", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
	#return PluginDescriptor(name="ProjectValerieSync", description="syncs", where = PluginDescriptor.WHERE_WIZARD, fnc=main)
