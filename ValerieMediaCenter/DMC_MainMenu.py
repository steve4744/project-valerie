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
from DMC_Global import getBoxtype, getAPILevel
from DMC_Movies import PVMC_Movies
from DMC_Series import PVMC_Series

from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin, registerPlugin
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

#dSize = getDesktop(0).size()
font = "/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/mayatypeuitvg.ttf"
#if dSize.width() == 720 and dSize.height() == 576:
#	font = "/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/blackSwan/mayatypeuitvg_4.3.ttf"
printl("Loading Font: " + font)
try:
	addFont(font, "Modern", 100, False)
except Exception, ex: #probably just openpli
	printl("Exception(" + str(type(ex)) + "): " + str(ex), "DMC_MainMenu::", "W")
	addFont(font, "Modern", 100, False, 0)

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

	def __init__(self, session):
		from Components.Sources.StaticText import StaticText
		Screen.__init__(self, session)
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))

		ConfigListScreen.__init__(self, [])
		self.initConfigList()
		#config.mediaplayer.saveDirOnExit.addNotifier(self.initConfigList)

		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"green": self.keySave,
			"red": self.keyCancel,
			"cancel": self.keyCancel,
			"ok": self.ok,
		}, -2)
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("Settings"))

	def initConfigList(self, element=None):
		printl("", self)
		try:
			self.list = []
			self.list.append(getConfigListEntry(_("Show wizard on next start"), config.plugins.pvmc.showwizard))
			self.list.append(getConfigListEntry(_("Start Valerie on e2 start"), config.plugins.pvmc.autostart))
			self.list.append(getConfigListEntry(_("Check for updates on Valerie start"), config.plugins.pvmc.checkforupdate))
			self.list.append(getConfigListEntry(_("Backdrop quality"), config.plugins.pvmc.backdropquality))
			self.list.append(getConfigListEntry(_("Skin"), config.plugins.pvmc.skin))
			self.list.append(getConfigListEntry(_("On Power press"), config.plugins.pvmc.onpowerpress))
			self.list.append(getConfigListEntry(_("Show Movie and TVShow in main menu"), config.plugins.pvmc.showmovieandtvinmainmenu))
			
			#self.list.append(getConfigListEntry(_("Use Trakt.tv"), config.plugins.pvmc.trakt))
			#self.list.append(getConfigListEntry(_("Trakt.tv - Username"), config.plugins.pvmc.traktuser))
			#self.list.append(getConfigListEntry(_("Trakt.tv - Password"), config.plugins.pvmc.traktpass))

			plugins = getPlugins(where=Plugin.SETTINGS)
			for plugin in plugins:
				pluginSettingsList = plugin.fnc()
				for pluginSetting in pluginSettingsList:
					self.list.append(getConfigListEntry("[" + plugin.name + "] " + pluginSetting[0], pluginSetting[1]))
			
			self.list.append(getConfigListEntry(_("[EXPERT] Valerie Config folder (Database, ...)"), config.plugins.pvmc.configfolderpath))
			self.list.append(getConfigListEntry(_("[EXPERT] Valerie media folder (Poster, Backdrops)"), config.plugins.pvmc.mediafolderpath))
			self.list.append(getConfigListEntry(_("[EXPERT] Valerie tmp folder (Logs, Cache)"), config.plugins.pvmc.tmpfolderpath))
			
			self["config"].setList(self.list)
		except Exception, ex:
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")

	def ok(self):
		printl("", self)

	def keySave(self):
		ConfigListScreen.keySave(self)

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
		
		self.onFirstExecBegin.append(self.update)

	# RTV = 0 opkg install successfull
	# RTV = 1 bianry found but no cmdline given
	# RTV = 127 Binary not found
	# RTV = 255 ERROR
	def update(self):
		self["text"].setText(_("Updating ProjectValerie...\n\n\nStay tuned :-)"))
		cmd = """
BIN=""
ipkg > /dev/null 2>/dev/null
if [ $? == "1" ]; then
 BIN="ipkg"
else
 opkg > /dev/null 2>/dev/null
 if [ $? == "1" ]; then
  BIN="opkg"
 fi
fi
echo "Binary: $BIN"

if [ $BIN != "" ]; then
 $BIN remove project-valerie
 echo "Cleaning up"
 rm -rf /usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie*
 $BIN install %s
fi""" % str(self.url)
		
		printl("cmd=" + str(cmd), self, "D")
		self.session.open(SConsole,"Excecuting command:", [cmd] , self.finishupdate)

	def finishupdate(self):
		time.sleep(2)
		self.session.openWithCallback(self.e2restart, MessageBox,_("Enigma2 must be restarted!\nShould Enigma2 now restart?"), MessageBox.TYPE_YESNO)

	def e2restart(self, answer):
		if answer is True:
			quitMainloop(3)
		else:
			self.close()

class PVMC_MainMenu(Screen):

	ShowStillPicture = False

	def __init__(self, isAutostart, session):
		printl("-> isAutostart=" + str(isAutostart), self)
		
		Screen.__init__(self, session)
		self.isAutostart = isAutostart
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		printl("self.oldService=" + str(self.oldService), self)
		self.session.nav.stopService()

		self.APILevel = getAPILevel(self)
		printl("self.APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()

		if self.APILevel >= 2:
			try:
				from StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel >= 2:
			self.UseDreamScene = ""
			try:
				self.UseDreamScene = DataElement().getDataPreloading(self, "stillpicture_usedreamscene")
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
				self.UseDreamScene = ""
			
			printl("self.UseDreamScene=" + str(self.UseDreamScene), self)
			if len(self.UseDreamScene) > 4:
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
		elif self.APILevel == 2:
			list = []
			list.append((_("Settings"), "PVMC_Settings", "menu_settings", "50"))
			list.append((_("Synchronize"), "PVMC_Sync",     "menu_sync", "50"))
			list.append((_("Live TV"),  "InfoBar",       "menu_tv", "50"))
			list.append((_("Movies"),   "PVMC_Movies",   "menu_movies", "50"))
			list.append((_("TV Shows"), "PVMC_Series",   "menu_series", "50"))
			
			self["menu"] = List(list, True)
			
			self["version"] = Label(config.plugins.pvmc.version.value)
		
		elif self.APILevel >= 3:
			list = []
			plugins = getPlugins(where=Plugin.MENU_PICTURES)
			if plugins is not None and len(plugins) == 1:
				list.append((_("Pictures"), plugins[0], "menu_pictures", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("Pictures >"), plugins, "menu_pictures", "50"))
			
			plugins = getPlugins(where=Plugin.MENU_MUSIC)
			if plugins is not None and len(plugins) == 1:
				list.append((_("Music"), plugins[0], "menu_music", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("Music >"), plugins, "menu_music", "50"))
			
			list.append((_("Live TV"),  "InfoBar", "menu_tv", "50"))
			
			if config.plugins.pvmc.showmovieandtvinmainmenu.value is True:
				list.append((_("Movies"),   "PVMC_Movies","", "50"))
				list.append((_("TV Shows"), "PVMC_Series", "", "50"))
			
			plugins = getPlugins(where=Plugin.MENU_VIDEOS)
			if plugins is not None and len(plugins) == 1:
				list.append((_("Videos"), plugins[0], "menu_videos", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("Videos >"), plugins, "menu_videos", "50"))
			
			plugins = getPlugins(where=Plugin.MENU_PROGRAMS)
			if plugins is not None and len(plugins) == 1:
				list.append((_("Programs"), plugins[0], "menu_programs", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("Programs >"), plugins, "menu_programs", "50"))
			
			plugins = getPlugins(where=Plugin.MENU_SYSTEM)
			if plugins is not None and len(plugins) == 1:
				list.append((_("System"), plugins[0], "menu_system", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("System >"), plugins, "menu_system", "50"))
			
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
		
		printl("<-", self)


	def onExec(self):
		if self.APILevel == 1:
			self["menu"].setIndex(0)
		elif self.APILevel >= 2:
			self["menu"].setIndex(2)
		
		if self.APILevel >= 2 and self.ShowStillPicture is True and len(self.UseDreamScene) > 0:
			printl("Using DreamScene at " + str(self.UseDreamScene), self)
			if os.access(self.UseDreamScene, os.F_OK) is True:
				self["showiframe"].setStillPicture(self.UseDreamScene, True, False, True)
			else:
				printl("Using DreamScene failed", self, "W")

	def onExecStartScript(self):
		printl("->", self)
		
		doUpdate = False
		
		if config.plugins.pvmc.checkforupdate.value == True:
			doUpdate = self.checkForUpdate()
		
		printl("doUpdate=" + str(doUpdate), self)
		
		if doUpdate is False:
			self.runAutostart()
		printl("<-",self)

	def runAutostart(self):
		printl("->", self)
		try:
			import os
			os.system("chmod 777 " + config.plugins.pvmc.configfolderpath.value + "start.sh")
			os.system("/bin/sh " + config.plugins.pvmc.configfolderpath.value + "start.sh")
		except Exception, e:
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		plugins = getPlugins(where=Plugin.AUTOSTART)
		for plugin in plugins:
			plugin.fnc(self.session)
		
		printl("<-", self)

	def power(self):
		import Screens.Standby
		if config.plugins.pvmc.onpowerpress.value == "Standby":
			self.session.open(Screens.Standby.Standby)
		else:
			self.session.open(Screens.Standby.TryQuitMainloop, 1)

	def checkForUpdate(self):
		box = getBoxtype()
		printl("box=" + str(box), self)
		self.url = config.plugins.pvmc.url.value + config.plugins.pvmc.updatexml.value
		printl("Checking URL: " + str(self.url), self) 
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
					if url.getAttribute("version") is None or url.getAttribute("version") == box[3]:
						self.remoteurl = url.childNodes[0].data
			
			printl("""Version: %s - URL: %s""" % (remoteversion, self.remoteurl), self)
			
			if config.plugins.pvmc.version.value != remoteversion and self.remoteurl != "":
				self.session.openWithCallback(self.startUpdate, MessageBox, \
					_("A new version of MediaCenter is available for download!\n\nVersion: %s") % remoteversion, \
					MessageBox.TYPE_YESNO, timeout=120, close_on_any_key=False, default=False)
				return True
		
		except Exception, e:
			printl("""Could not download HTTP Page (%s)""" % (e), self, "E")
		return False

	def startUpdate(self, answer):
		if answer is True:
			self.session.open(PVMC_Update, self.remoteurl)
		else:
			self.runAutostart()

	def Error(self, error):
		self.session.open(MessageBox,_("UNEXPECTED ERROR:\n%s") % (error), MessageBox.TYPE_INFO)

	def showStillPicture(self):
		return

	def okbuttonClick(self):
		printl("", self)
		
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
			printl("selection=" + str(selection), self)
			if selection is not None:
				printl("type(selection[1])=" + str(type(selection[1])), self)
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
					self.session.openWithCallback(self.showStillPicture, PVMC_Settings)
				elif selection[1] == "PVMC_Sync":
					isInstalled = False
					try:
						from Plugins.Extensions.ProjectValerieSync.plugin import ProjectValerieSync
						isInstalled = True
					except Exception, ex:
						isInstalled = False
						printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
					if isInstalled:
						self.session.openWithCallback(self.showStillPicture, ProjectValerieSync)
					else:
						self.session.open(MessageBox, _("Please install the plugin \nProjectValerieSync\n to use this feature."), type = MessageBox.TYPE_INFO)
				elif selection[1] == "InfoBar":
					self.Exit()
				elif selection[1] == "Exit":
					self.Exit()
				else:
					if self.APILevel >= 3:
						s = selection[1]
						if  type(s) is list:
							self.menu_main_list_index = self["menu"].getIndex()
							self.menu_main_list = self["menu"].list
							l = []
							l.append(("< " + _("Back"), Plugin.MENU_MAIN, "", "50"))
							for plugin in s:
								l.append((plugin.name, plugin, "", "50"))
							self["menu"].setList(l)
							self["menu"].setIndex(1)
						elif type(s) is int:
							if s == Plugin.MENU_MAIN:
								self["menu"].setList(self.menu_main_list)
								self["menu"].setIndex(self.menu_main_list_index)
						elif type(s) is not str:
							if s.supportStillPicture is False:
								if self.APILevel >= 2 and self.ShowStillPicture is True:
									self["showiframe"].finishStillPicture()
							if s.start is not None:
								self.session.openWithCallback(self.showStillPicture, s.start)
							elif s.fnc is not None:
								s.fnc(self.session)

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
		printl("self.oldService=" + str(self.oldService), self)
		self.session.nav.playService(self.oldService)
		
		if self.isAutostart:
			self. close()
		else:
			self.close((True,) )

registerPlugin(Plugin(name=_("Settings"), start=PVMC_Settings, where=Plugin.MENU_SYSTEM, supportStillPicture=True))