# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.MenuList import MenuList
from Components.Sources.List import List
from Screens.ChoiceBox import ChoiceBox
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen

from DataElement import DataElement

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin

#------------------------------------------------------------------------------------------

import gettext
import os
from Components.Language import language
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, SCOPE_LANGUAGE

def localeInit():
	lang = language.getLanguage()
	os.environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ProjectValerie", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ProjectValerie/locale/"))

def _(txt):
	t = gettext.dgettext("ProjectValerie", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#------------------------------------------------------------------------------------------

def getViews():
	return ("DMC_ListView", "DMC_PosterView")

def getViewClass():
	return DMC_View

class DMC_View(Screen, HelpableScreen):

	skin = """
	<screen name="DMC_View" position="0,0" size="1280,720" title=" " flags="wfNoBorder" backgroundColor="#ff000000">
<widget name="API" text="1" position="0,0" zPosition="0" size="1,1"/>
<widget name="listview_itemsperpage" text="12" position="0,0" zPosition="0" size="1,1" />
<widget source="listview" render="Listbox" zPosition="3" position="106,181" size="391,390" scrollbarMode="showNever" transparent="0" backgroundColor="#10303030" backgroundColorSelected="#0018587A">
<convert type="TemplatedMultiContent">
 {"template": [ MultiContentEntryText(pos = (0,0), size = (373,32), flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 0) ], "fonts": [gFont("Modern", 20)], "itemHeight": 32, "scrollbarMode": "showNever" } 
</convert>
</widget>
</screen>
	"""

	ON_CLOSED_CAUSE_CHANGE_VIEW = 1

	FAST_STILLPIC = False

	def __init__(self, session, libraryName, loadLibrary, playEntry, skinName="DMC_View"):
		self.skinName = skinName
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = skinName
		
		self.libraryName = libraryName
		self.loadLibrary = loadLibrary
		self._playEntry = playEntry
		
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		
		# Initialise API Level for this screen
		self.APILevel = 1 
		try:
			self.APILevel = int(DataElement().getDataPreloading(self, "API"))
		except Exception, ex:
			printl(str(ex))
			self.APILevel = 1
		
		printl("APILevel=" + str(self.APILevel))
		
		if self.APILevel >= 2:
			self["API"] = DataElement()
		
		# Initialise library list
		list = []
		if self.APILevel == 1:
			self["listview"] = MenuList(list)
		elif self.APILevel >= 2:
			self["listview"] = List(list, True)
			self["listview_itemsperpage"] = DataElement()
		
		self["actions"] = HelpableActionMap(self, "DMC_View", 
		{
			"ok":         (self.onKeyOk, ""),
			"cancel":     (self.onKeyCancel, ""),
			"left":       (self.onKeyLeft, ""),
			"right":      (self.onKeyRight, ""),
			"left_quick": (self.onKeyLeftQuick, ""),
			"right_quick": (self.onKeyRightQuick, ""),
			"up":         (self.onKeyUp, ""),
			"down":       (self.onKeyDown, ""),
			"up_quick":   (self.onKeyUpQuick, ""),
			"down_quick": (self.onKeyDownQuick, ""),
			"info":       (self.onKeyInfo, ""),
			"menu":       (self.onKeyMenu, ""),

			"red":        (self.onKeyRed, ""),
			"yellow":     (self.onKeyYellow, ""),
			"green":      (self.onKeyGreen, ""),
			"blue":       (self.onKeyBlue, ""),

		}, -2)
		
		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.onFirstExec)

	def setCustomTitle(self):
		self.setTitle(_(self.libraryName))

	def onFirstExec(self):
		self._load()
		self.refresh()

	def onKeyOk(self):
		self.onEnter()

	def onKeyCancel(self):
		self.onLeave()

	def onKeyInfo(self):
		pass

	def onKeyMenu(self):
		self.displayPluginsMenu()

	def onKeyLeft(self):
		pass
	def onKeyRight(self):
		pass

	def onKeyLeftQuick(self):
		pass
	def onKeyRightQuick(self):
		pass

	def onKeyUp(self):
		self.onPreviousEntry()

	def onKeyDown(self):
		self.onNextEntry()

	def onKeyUpQuick(self):
		self.onPreviousEntryQuick()

	def onKeyDownQuick(self):
		self.onNextEntryQuick()

	def onKeyRed(self):
		pass
	def onKeyYellow(self):
		pass
	def onKeyGreen(self):
		pass
	def onKeyBlue(self):
		self.onToggleView()

	def onToggleView(self):
		self.close((DMC_View.ON_CLOSED_CAUSE_CHANGE_VIEW, ))

	def onNextEntry(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def onNextEntryQuick(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].down()
		elif self.APILevel >= 2:
			self["listview"].selectNext()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def onPreviousEntry(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def onPreviousEntryQuick(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].up()
		elif self.APILevel >= 2:
			self["listview"].selectPrevious()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def onNextPage(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].pageDown()
		elif self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			index = self["listview"].getIndex() + itemsPerPage
			if index >= itemsTotal:
				index = itemsTotal - 1
			self["listview"].setIndex(index)
		self.refresh()

	def onPreviousPage(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].pageUp()
		elif self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			index = self["listview"].getIndex() - itemsPerPage
			if index < 0:
				index = 0
			self["listview"].setIndex(index)
		self.refresh()

	onEnterPrimaryKeys = None
	onLeavePrimaryKeyValuePair = None
	onLeaveSelectKeyValuePair = None
	currentKeyValuePair = None

	def onEnter(self):
		printl("", self, "D")
		selection = self["listview"].getCurrent()
		if selection is not None:
			print "selection", selection
			primaryKeyValuePair = None
			if self.onEnterPrimaryKeys is not None:
				if "play" in self.onEnterPrimaryKeys:
					printl("playEntry ->", self, "D")
					self.playEntry(selection[1])
					printl("playEntry <-", self, "D")
					return
				else:
					primaryKeyValuePair = {}
					for key in self.onEnterPrimaryKeys:
						primaryKeyValuePair[key] = selection[1][key]
			self._load(primaryKeyValuePair)
			#self["listview"].setIndex(0)
		self.refresh()

	def onLeave(self):
		selectKeyValuePair = self.onLeaveSelectKeyValuePair
		print selectKeyValuePair
		if selectKeyValuePair is None:
			self.close()
			return
		
		self._load(self.onLeavePrimaryKeyValuePair)
		for i in range(len(self.listViewList)):
			entry = self.listViewList[i][1]
			print i, entry
			isIndex = True
			
			for key in selectKeyValuePair.keys():
				if entry[key] != selectKeyValuePair[key]:
					isIndex = False
					break
			if isIndex:
				self["listview"].setIndex(i)
				break
		self.refresh()

	def _load(self, primaryKeys=None):
		print "primaryKeys", primaryKeys
		self.currentKeyValuePair = primaryKeys
		library = self.loadLibrary(primaryKeys)
		self.listViewList = library[0]
		#print self.listViewList
		self.onEnterPrimaryKeys = library[1]
		self.onLeavePrimaryKeyValuePair = library[2]
		self.onLeaveSelectKeyValuePair = library[3]
		
		print "onEnterPrimaryKeys", self.onEnterPrimaryKeys
		print "onLeavePrimaryKeyValuePair", self.onLeavePrimaryKeyValuePair
		print "onLeaveSelectKeyValuePair", self.onLeaveSelectKeyValuePair
		
		self.listViewList.sort(key=lambda x: x[2])
		self["listview"].setList(self.listViewList)
		self["listview"].setIndex(0)

	def setText(self, name, value, ignore=False, what=None):
		try:
			if self[name]:
				if len(value) > 0:
					self[name].setText(value)
				elif ignore is False:
					if what is None:
						self[name].setText(_("Not available"))
					else:
						self[name].setText(what + ' ' + _("not available"))
				else:
					self[name].setText(" ")
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def refresh(self, changeBackdrop=True):
		selection = self["listview"].getCurrent()
		if selection is not None:
			self._refresh(selection, changeBackdrop)

	def _refresh(self, selection, changeBackdrop):
		pass

	def playEntry(self, entry):
		if self._playEntry(entry) is False:
			title = _("Not found!\n")
			text = entry["Path"] + _("\n\nPlease make sure that your drive is connected/mounted.")
			self.session.open(MessageBox, title + text, type = MessageBox.TYPE_ERROR)

	def displayPluginsMenu(self):
		pluginList = []
		plugins = getPlugins(where=Plugin.MENU_MOVIES_PLUGINS)
		for plugin in plugins:
			pluginList.append((plugin.name, plugin.start, ))
		
		if len(pluginList) == 0:
			pluginList.append((_("No plugins available"), None, ))
		
		self.session.openWithCallback(self.displayPluginsMenuCallback, ChoiceBox, \
			title=_("Plugins"), list=pluginList)

	def displayPluginsMenuCallback(self, choice):
		if choice is None or choice[1] is None:
			return
		
		selection = self["listview"].getCurrent()
		if selection is not None:
			self.session.open(choice[1], selection[1])


