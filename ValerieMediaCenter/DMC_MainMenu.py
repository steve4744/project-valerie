# -*- coding: utf-8 -*-

import gettext
import os
import time
import urllib2
from twisted.web.microdom import parseString

from enigma import eListboxPythonMultiContent, gFont, eTimer, eDVBDB, getDesktop, quitMainloop, getDesktop, addFont
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.AVSwitch import AVSwitch
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Console import Console
from Components.FileList import FileList
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.Console import Console as SConsole
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_PLUGINS, SCOPE_LANGUAGE

from DataElement import DataElement
from DMC_Global import printl, getBoxtype, getAPILevel
from DMC_Movies import PVMC_Movies
from DMC_Series import PVMC_Series

#------------------------------------------------------------------------------------------

try:
	addFont("/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/mayatypeuitvg.ttf", "Modern", 100, False)
except Exception, ex: #probably just openpli
	print ex
	addFont("/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/mayatypeuitvg.ttf", "Modern", 100, False, 0)

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


localeInit()
language.addCallback(localeInit)

#------------------------------------------------------------------------------------------

class PVMC_Settings(Screen, ConfigListScreen):
	skinDeprecated = """
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
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel))
		if self.APILevel >= 2:
			self["API"] = DataElement()
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
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
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("Settings"))

	def initConfigList(self, element=None):
		print "[initConfigList]", element
		try:
			self.list = []
			self.list.append(getConfigListEntry(_("Show wizard on next start"), config.plugins.pvmc.showwizard))
			self.list.append(getConfigListEntry(_("Start Valerie on e2 start"), config.plugins.pvmc.autostart))
			self.list.append(getConfigListEntry(_("Check for updates on Valerie start"), config.plugins.pvmc.checkforupdate))
			self.list.append(getConfigListEntry(_("Backdrop quality"), config.plugins.pvmc.backdropquality))
			self.list.append(getConfigListEntry(_("Skin"), config.plugins.pvmc.skin))
			
			self.list.append(getConfigListEntry(_("Use Trakt.tv"), config.plugins.pvmc.trakt))
			self.list.append(getConfigListEntry(_("Trakt.tv - Username"), config.plugins.pvmc.traktuser))
			self.list.append(getConfigListEntry(_("Trakt.tv - Password"), config.plugins.pvmc.traktpass))

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
	<screen position="center,center" size="500,380" title="Software Update">
	<widget name="text" position="10,10" size="480,360" font="Regular;22" halign="center" valign="center"/>
	</screen>"""

	def __init__(self, session, remoteurl):
		self.skin = PVMC_Update.skin
		Screen.__init__(self, session)
		
		self.working = False
		self.Console = Console()
		self["text"] = ScrollLabel(_("Checking for updates ..."))
		
		self["actions"] = NumberActionMap(["WizardActions", "InputActions", "EPGSelectActions"],
		{
			"ok": self.close,
			"back": self.close
		}, -1)
		
		self.url = remoteurl
		
		self.onFirstExecBegin.append(self.initupdate)

	def checkIpkg(self, result, retval, extra_args):
		if retval == 1:
			self.initupdate("ipkg")
		else:
			self.initupdate("opkg")

	def initupdate(self, bin="test"):
		
		if bin == "test":
			cmd = "ipkg"
			self.Console.ePopen(cmd, self.checkIpkg)
			return
		
		self["text"].setText(_("Updating ProjectValerie...\n\n\nStay tuned :-)"))
		cmd = " install -force-overwrite " + str(self.url)
		print bin, cmd
		self.session.open(SConsole,"Excecuting command: " + bin, [bin + cmd] , self.finishupdate)

	def finishupdate(self):
		time.sleep(2)
		self.session.openWithCallback(self.e2restart, MessageBox,_("Enigma2 must be restarted!\nShould Enigma2 now restart?"), MessageBox.TYPE_YESNO)
		#self.session.open(MessageBox,_("Enigma2 will now restart!"),  MessageBox.TYPE_INFO)
		#time.sleep(4)
		#quitMainloop(3)

	def e2restart(self, answer):
		if answer is True:
			quitMainloop(3)
		else:
			self.close()

class PVMC_MainMenu(Screen):

	ShowStillPicture = False

	def __init__(self, isAutostart, session):
		printl("PVMC_MainMenu:__init__")
		print "PVMC_MainMenu:__init__", isAutostart
		
		Screen.__init__(self, session)
		self.isAutostart = isAutostart
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		print "OLDSERVICE", self.oldService
		self.session.nav.stopService()

		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel))
		if self.APILevel >= 2:
			self["API"] = DataElement()

		if self.APILevel >= 2:
			try:
				from StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				print ex
		
		if self.APILevel >= 2:
			self.UseDreamScene = ""
			try:
				self.UseDreamScene = DataElement().getDataPreloading(self, "stillpicture_usedreamscene")
			except Exception, ex:
				printl(str(ex))
				self.UseDreamScene = ""
			
			printl("UseDreamScene=" + str(self.UseDreamScene))
			if len(self.UseDreamScene) > 0:
				self["stillpicture_usedreamscene"] = DataElement()
		
		if self.APILevel == 1:
			list = []
			list.append((_("Movies"), "PVMC_Watch", "menu_watch", "50"))
			list.append((_("TV"), "InfoBar", "menu_tv", "50"))
			list.append((_("Settings"), "PVMC_Settings", "menu_settings", "50"))
			list.append((_("Synchronize"), "PVMC_Sync", "menu_sync", "50"))
			list.append((_("Music"), "PVMC_AudioPlayer", "menu_music", "50"))
			self["menu"] = List(list, True)
			
			listWatch = []
			listWatch.append((" ", "dummy", "menu_dummy", "50"))
			listWatch.append((_("Movies"), "PVMC_Movies", "menu_movies", "50"))
			listWatch.append((_("Series"), "PVMC_Series", "menu_series", "50"))
			self["menuWatch"] = List(listWatch, True)
			self.Watch = False
		elif self.APILevel >= 2:
			list = []
			list.append((_("Settings"), "PVMC_Settings", "menu_settings", "50"))
			list.append((_("Synchronize"),     "PVMC_Sync",     "menu_sync", "50"))
			list.append((_("Live TV"),  "InfoBar",       "menu_tv", "50"))
			list.append((_("Movies"),   "PVMC_Movies",   "menu_movies", "50"))
			list.append((_("TV Shows"), "PVMC_Series",   "menu_series", "50"))
			self["menu"] = List(list, True)
			
			self["version"] = Label(config.plugins.pvmc.version.value)
		
		self["title"] = StaticText("")
		self["welcomemessage"] = StaticText("")
		
		self.inter = 0
		
		self["actions"] = HelpableActionMap(self, "PVMC_MainMenuActions", 
			{
				"ok": self.okbuttonClick,
				"left": self.left,
				"right": self.right,
				"up": self.up,
				"down": self.down,
				"power": self.power,
			}, -1)
		
		if self.isAutostart is False and self.APILevel >= 2:
			self["cancelActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.Exit,
			}, -1)
		elif self.APILevel == 1:
			self["cancelActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.cancel,
			}, -1)
		
		self.onFirstExecBegin.append(self.onExec)
		# Executes a start script
		self.onFirstExecBegin.append(self.onExecStartScript)
		
		if config.plugins.pvmc.checkforupdate.value == True:
			self.onFirstExecBegin.append(self.checkForUpdate)
		


	def onExec(self):
		if self.APILevel == 1:
			self["menu"].setIndex(0)
		elif self.APILevel >= 2:
			self["menu"].setIndex(2)

	def onExecStartScript(self):
		printl("PVMC_MainMenu::onExecStartScript ->")
		try:
			import os
			os.system("chmod 777 /hdd/valerie/start.sh")
			os.system("/bin/sh /hdd/valerie/start.sh")
		except Exception, e:
			printl("Exception: " + str(e))
		printl("PVMC_MainMenu::onExecStartScript <-")
		
		if self.APILevel >= 2 and self.ShowStillPicture is True and len(self.UseDreamScene) > 0:
			printl("Using DreamScene at " + self.UseDreamScene)
			if os.access(self.UseDreamScene, os.F_OK) is True:
				self["showiframe"].setStillPicture(self.UseDreamScene, True, False, True)
			#self["showiframe"].setStillPicture("/mnt/nfs/Development/1/blue.mp4", True, False, True)

	def power(self):
		import Screens.Standby
		self.session.open(Screens.Standby.TryQuitMainloop, 1)

	def checkForUpdate(self):
		box = getBoxtype()
		printl(box)
		self.url = config.plugins.pvmc.url.value + config.plugins.pvmc.updatexml.value
		printl("Checking URL: " + self.url) 
		try:
			opener = urllib2.build_opener()
			box = getBoxtype()
			opener.addheaders = [('User-agent', 'urllib2_val_' + box[1] + '_' + box[2] + '_' + box[3])]
			f = opener.open(self.url)
			#f = urllib2.urlopen(self.url)
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
				self.session.openWithCallback(self.startUpdate, MessageBox,_("A new version of MediaCenter is available for download!\n\nVersion: %s") % remoteversion, MessageBox.TYPE_YESNO)
		
		except Exception, e:
			print """Could not download HTTP Page (%s)""" % e

	def startUpdate(self, answer):
		if answer is True:
			self.session.open(PVMC_Update, self.remoteurl)

	def Error(self, error):
		self.session.open(MessageBox,_("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)

	def showStillPicture(self):
		return

	def okbuttonClick(self):
		print "okbuttonClick"
		
		if self.APILevel == 1 and self.Watch == True:
			selection = self["menuWatch"].getCurrent()
			if selection is not None:
				if selection[1] == "PVMC_Movies":
					if self.APILevel >= 2 and self.ShowStillPicture is True:
						self["showiframe"].finishStillPicture()
					self.session.openWithCallback(self.showStillPicture, PVMC_Movies)
				elif selection[1] == "PVMC_Series":
					if self.APILevel >= 2 and self.ShowStillPicture is True:
						self["showiframe"].finishStillPicture()
					self.session.openWithCallback(self.showStillPicture, PVMC_Series)
		else:
			selection = self["menu"].getCurrent()
			print "SELECTION", selection
			if selection is not None:
				if selection[1] == "PVMC_Watch":
					self["menuWatch"].setIndex(1)
					self.Watch = True;
				elif selection[1] == "PVMC_Movies":
					if self.APILevel >= 2 and self.ShowStillPicture is True:
						self["showiframe"].finishStillPicture()
					self.session.openWithCallback(self.showStillPicture, PVMC_Movies)
				elif selection[1] == "PVMC_Series":
					if self.APILevel >= 2 and self.ShowStillPicture is True:
						self["showiframe"].finishStillPicture()
					self.session.openWithCallback(self.showStillPicture, PVMC_Series)
				elif selection[1] == "PVMC_AudioPlayer":
					self.session.open(MessageBox, "TODO!\nThis feature is not yet implemented.", type = MessageBox.TYPE_INFO)
					#self.session.open(MC_AudioPlayer)
				elif selection[1] == "PVMC_Settings":
					self.session.openWithCallback(self.showStillPicture, PVMC_Settings, self)
				elif selection[1] == "PVMC_Sync":
					isInstalled = False
					try:
						from Plugins.Extensions.ProjectValerieSync.plugin import ProjectValerieSync
						isInstalled = True
					except Exception, ex:
						isInstalled = False
						print "Exception: ", ex
					if isInstalled:
						self.session.openWithCallback(self.showStillPicture, ProjectValerieSync)
					else:
						self.session.open(MessageBox, _("Please install the plugin \nProjectValerieSync\n to use this feature."), type = MessageBox.TYPE_INFO)
				elif selection[1] == "InfoBar":
					self.Exit()
				elif selection[1] == "Exit":
					self.Exit()

	def up(self):
		if self.APILevel == 1:
			self.cancel()
		elif self.APILevel >= 2:
			self["menu"].selectPrevious()
		return

	def down(self):
		if self.APILevel == 1:
			self.okbuttonClick()
		elif self.APILevel >= 2:
			self["menu"].selectNext()
		return

	def right(self):
		if self.APILevel == 1:
			if self.Watch == True:
				self["menuWatch"].selectNext()
				if self["menuWatch"].getIndex() == 0:
					self["menuWatch"].selectNext()
			else:
				self["menu"].selectNext()

	def left(self):
		if self.APILevel == 1:
			if self.Watch == True:
				self["menuWatch"].selectPrevious()
				if self["menuWatch"].getIndex() == 0:
					self["menuWatch"].selectPrevious()
			else:
				self["menu"].selectPrevious()

	def cancel(self):
		if self.APILevel == 1:
			if self.Watch == True:
				self["menuWatch"].setIndex(0)
				self.Watch = False;
		
		return

	def Exit(self):
		if self.APILevel >= 2 and self.ShowStillPicture is True:
			self["showiframe"].finishStillPicture()
		print "OLDSERVICE", self.oldService
		self.session.nav.playService(self.oldService)
		
		if self.isAutostart:
			self. close()
		else:
			self.close((True,) )
