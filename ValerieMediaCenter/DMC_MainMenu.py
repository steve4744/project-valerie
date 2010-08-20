from enigma import eListboxPythonMultiContent, gFont, eTimer, eDVBDB, getDesktop
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Console import Console
from Components.ScrollLabel import ScrollLabel

from Components.ConfigList import ConfigList
from Components.config import *

from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch

from Components.ConfigList import ConfigListScreen

import os

from enigma import quitMainloop

# Plugins
from DMC_Movies import PVMC_Movies
from DMC_Series import PVMC_Series


from Components.MenuList import MenuList
from DMC_Global import printl, getBoxtype

import urllib2
# Unfortunaly not everyone has twisted installed ...
try:
	from twisted.web.microdom import parseString
except Exception, e:
	printl("import twisted.web.microdom failed")

#------------------------------------------------------------------------------------------
	
class Settings(Screen, ConfigListScreen):
	skin = """
		<screen name="PVMC_Settings" position="160,150" size="450,200" title="Settings">
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="300,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="10,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="300,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" position="10,44" size="430,146" />
		</screen>"""

	def __init__(self, session, parent):
		from Components.Sources.StaticText import StaticText
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))

		ConfigListScreen.__init__(self, [])
		self.parent = parent
		self.initConfigList()
		#config.mediaplayer.saveDirOnExit.addNotifier(self.initConfigList)

		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
		    "green": self.save,
		    "red": self.cancel,
		    "cancel": self.cancel,
		    "ok": self.ok,
		}, -2)

	def initConfigList(self, element=None):
		print "[initConfigList]", element
		try:
			self.list = []
			self.list.append(getConfigListEntry(_("showwizard"), config.plugins.pvmc.showwizard))
			self.list.append(getConfigListEntry(_("autostart"), config.plugins.pvmc.autostart))
			self.list.append(getConfigListEntry(_("checkforupdate"), config.plugins.pvmc.checkforupdate))
			self.list.append(getConfigListEntry(_("uselocal"), config.plugins.pvmc.uselocal))
			self["config"].setList(self.list)
		except KeyError:
			print "keyError"

	def changedConfigList(self):
		self.initConfigList()

	def ok(self):
		print "ok"

	def LocationBoxClosed(self, path):
		print "PathBrowserClosed:", path
		#if path is not None:
		#	config.mediaplayer.defaultDir.setValue(path)

	def save(self):
		print "save"
		for x in self["config"].list:
			x[1].save()
		self.close()

	def cancel(self):
		self.close()



class PVMC_Update(Screen):
	skin = """
		<screen position="100,100" size="500,380" title="Software Update" >
			<widget name="text" position="10,10" size="480,360" font="Regular;22" />
		</screen>"""

	def __init__(self, session, remoteurl):
		self.skin = PVMC_Update.skin
		Screen.__init__(self, session)

		self.working = False
		self.Console = Console()
		self["text"] = ScrollLabel("Checking for updates ...")
		
		self["actions"] = NumberActionMap(["WizardActions", "InputActions", "EPGSelectActions"],
		{
			"ok": self.close,
			"back": self.close
		}, -1)
		
		self.url = remoteurl
		
		self.onFirstExecBegin.append(self.initupdate)

	def initupdate(self):
		self.working = True
		
		cmd = "ipkg install -force-overwrite " + str(self.url)
		
		self["text"].setText("Updating MediaCenter ...\n\n\nStay tuned :-)")
		self.Console.ePopen(cmd, self.startupdate)

	def startupdate(self, result, retval, extra_args):
		if retval == 0:
			self.working = True
			self["text"].setText(result)
			self.session.open(MessageBox,("Your MediaCenter was hopefully updated now ...\n\nEnigma will restart now!"),  MessageBox.TYPE_INFO)
			quitMainloop(3)
		else:
			self.working = False
			



class PVMC_MainMenu(Screen):
	def __init__(self, session):
		printl("PVMC_MainMenu:__init__")
		Screen.__init__(self, session)

		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()

	
		list = []
		list.append(("Movies", "PVMC_Watch", "menu_watch", "50"))
		list.append(("TV", "InfoBar", "menu_tv", "50"))
		#list.append(("TV", "Exit", "menu_exit", "50"))
		list.append(("Settings", "PVMC_Settings", "menu_settings", "50"))
		list.append(("Sync", "PVMC_Sync", "menu_sync", "50"))
		list.append(("Music", "PVMC_AudioPlayer", "menu_music", "50"))
		#list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list, True)

		listWatch = []
		listWatch.append((" ", "dummy", "menu_dummy", "50"))
		listWatch.append(("Movies", "PVMC_Movies", "menu_movies", "50"))
		listWatch.append(("Series", "PVMC_Series", "menu_series", "50"))
		#listWatch.append(("Series", "MC_VideoPlayer", "menu_watch_all", "50"))
		self["menuWatch"] = List(listWatch, True)
		self.Watch = False

		self["title"] = StaticText("")
		self["welcomemessage"] = StaticText("")

		#self["moveWatchMovies"] = MovingPixmap()
		#self["moveWatchSeries"] = MovingPixmap()

		self.inter = 0

		self["actions"] = HelpableActionMap(self, "PVMC_MainMenuActions", 
			{
				"ok": self.okbuttonClick,
				"cancel": self.cancel,
				"left": self.left,
				"right": self.right,
				"up": self.up,
				"down": self.down,
				"power": self.power,
			}, -1)

		if config.plugins.pvmc.checkforupdate.value == True:
			self.onFirstExecBegin.append(self.checkForUpdate)

	def power(self):
		import Screens.Standby
		self.session.open(Screens.Standby.TryQuitMainloop, 1)

	def checkForUpdate(self):
		box = getBoxtype()
		printl(box)
		self.url = config.plugins.pvmc.url.value + config.plugins.pvmc.updatexml.value
		printl("Checking URL: " + self.url) 
		try:
			f = urllib2.urlopen(self.url)
			html = f.read()
			dom = parseString(html)
			update = dom.getElementsByTagName("update")[0]
			stb = update.getElementsByTagName("stb")[0]
			version = stb.getElementsByTagName("version")[0]
			remoteversion = version.childNodes[0].data
			urls = stb.getElementsByTagName("url")
			self.remoteurl = ""
			for url in urls:
				if url.getAttribute("arch") == box[2]:
					printl(url.getAttribute("version"))
					if url.getAttribute("version") is None or url.getAttribute("version") == box[3]:
						self.remoteurl = url.childNodes[0].data
			
			printl("""Version: %s - URL: %s""" % (remoteversion, self.remoteurl))
			
			if config.plugins.pvmc.version.value != remoteversion and self.remoteurl != "":
				self.session.openWithCallback(self.startUpdate, MessageBox,_("""A new version of MediaCenter is available for download!\n\nVersion: %s""" % remoteversion), MessageBox.TYPE_YESNO)

		except Exception, e:
			print """Could not download HTTP Page (%s)""" % e


	def startUpdate(self, answer):
		if answer is True:
			self.session.open(PVMC_Update, self.remoteurl)

	def Error(self, error):
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)

	def okbuttonClick(self):
		print "okbuttonClick"

		if self.Watch == True:
			selection = self["menuWatch"].getCurrent()
			if selection is not None:
				if selection[1] == "PVMC_Movies":
					self.session.open(PVMC_Movies)
				elif selection[1] == "PVMC_Series":
					self.session.open(PVMC_Series)
		else:
			selection = self["menu"].getCurrent()
			if selection is not None:
				if selection[1] == "PVMC_Watch":
					self["menuWatch"].setIndex(2)
					self.Watch = True;
				elif selection[1] == "PVMC_AudioPlayer":
					self.session.open(MessageBox, "TODO!\nThis feature is not yet implemented.", type = MessageBox.TYPE_INFO)
					#self.session.open(MC_AudioPlayer)
				elif selection[1] == "PVMC_Settings":
					self.session.open(Settings, self)
				elif selection[1] == "PVMC_Sync":
					try:
						from Plugins.Extensions.ProjectValerieSync.plugin import ProjectValerieSync
						self.session.open(ProjectValerieSync)
					except Exception, ex:
						self.session.open(MessageBox, "Please install the plugin \nProjectValerieSync\n to use this feature.", type = MessageBox.TYPE_INFO)
					#self.session.open(Settings, self)
#					from Menu import MainMenu, mdom
#					menu = mdom.getroot()
#					assert menu.tag == "menu", "root element in menu must be 'menu'!"


#					self.session.open(MainMenu, menu)
				elif selection[1] == "InfoBar":
					self.Exit()
					#eDVBDB.getInstance().reloadBouquets()
					#from Screens.InfoBar import InfoBar
					#self.session.open(InfoBar)
				elif selection[1] == "Exit":
					self.Exit()

	def up(self):
		self.cancel()
		return

	def down(self):
		self.okbuttonClick()
		return

	def right(self):
		if self.Watch == True:
			self["menuWatch"].selectNext()
			if self["menuWatch"].getIndex() == 0:
				self["menuWatch"].selectNext()
		else:
			self["menu"].selectNext()

	def left(self):
		if self.Watch == True:
			self["menuWatch"].selectPrevious()
			if self["menuWatch"].getIndex() == 0:
				self["menuWatch"].selectPrevious()
		else:
			self["menu"].selectPrevious()

	def cancel(self):
		if self.Watch == True:
			self["menuWatch"].setIndex(0)
			self.Watch = False;

		return

	def Exit(self):
		self.close()

