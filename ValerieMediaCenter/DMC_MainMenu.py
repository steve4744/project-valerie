from enigma import eListboxPythonMultiContent, gFont, eTimer, eDVBDB, getDesktop
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.Console import Console as SConsole
from Components.Console import Console
from Components.ScrollLabel import ScrollLabel

from Components.ConfigList import ConfigList
from Components.config import *

from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch

from Components.ConfigList import ConfigListScreen

import os
import time

from enigma import quitMainloop, getDesktop

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

from enigma import addFont
try:
    addFont("/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/mayatypeuitvg.ttf", "Modern", 100, False)
except Exception, ex: #probably just openpli
    print ex
    addFont("/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/mayatypeuitvg.ttf", "Modern", 100, False, 0)  

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
#------------------------------------------------------------------------------------------
	
class PVMC_Settings(Screen, ConfigListScreen):
        try:
            sz_w = getDesktop(0).size().width()
        except:
            sz_w = 720
        if sz_w == 1280:
            skin = """
            <screen position="0,0" size="1280,720" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1280,720" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1280.png"/>
            <widget source="Title" render="Label" transparent="1" zPosition="1" halign="center" valign="center" position="60,30" size="1160,65" font="Modern;50" foregroundColor="#006CA4C5"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="1" position="60,660" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="1" position="280,660" size="15,16" alphatest="blend"/>
            <widget source="key_red" render="Label" position="80,652" zPosition="1" size="200,34" font="Modern;24" halign="left" valign="center" transparent="1"/>
            <widget source="key_green" render="Label" position="300,652" zPosition="1" size="200,34" font="Modern;24" halign="left" valign="center" transparent="1"/>
            <widget name="config" zPosition="1" position="60,140" size="1160,440" scrollbarMode="showOnDemand" transparent="1" enableWrapAround="1"/>
            </screen>"""
        elif sz_w == 1024:
            skin = """
            <screen position="0,0" size="1024,576" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="1024,576" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background1024.png"/>
            <widget source="Title" render="Label" transparent="1" zPosition="1" halign="center" valign="center" position="60,30" size="904,55" font="Modern;40" foregroundColor="#006CA4C5"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="1" position="60,516" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="1" position="280,516" size="15,16" alphatest="blend"/>
            <widget source="key_red" render="Label" position="80,508" zPosition="1" size="200,32" font="Modern;22" halign="left" valign="center" transparent="1"/>
            <widget source="key_green" render="Label" position="300,508" zPosition="1" size="200,32" font="Modern;22" halign="left" valign="center" transparent="1"/>
            <widget name="config" zPosition="1" position="60,100" size="904,200" scrollbarMode="showOnDemand" transparent="1" enableWrapAround="1"/>
            </screen>"""
        else:
            skin = """
            <screen position="0,0" size="720,576" title=" " flags="wfNoBorder">
            <ePixmap position="0,0" zPosition="-10" size="720,576" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/default/background720.png"/>
            <widget source="Title" render="Label" transparent="1" zPosition="1" halign="center" valign="center" position="60,30" size="600,45" font="Modern;30" foregroundColor="#006CA4C5"/>
            <ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="1" position="60,516" size="15,16" alphatest="blend"/>
            <ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="1" position="280,516" size="15,16" alphatest="blend"/>
            <widget source="key_red" render="Label" position="80,508" zPosition="1" size="200,30" font="Modern;20" halign="left" valign="center" transparent="1"/>
            <widget source="key_green" render="Label" position="300,508" zPosition="1" size="200,30" font="Modern;20" halign="left" valign="center" transparent="1"/>
            <widget name="config" zPosition="1" position="60,100" size="600,200" scrollbarMode="showOnDemand" transparent="1" enableWrapAround="1"/>
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
                self.onLayoutFinish.append(self.setCustomTitle)
                
        def setCustomTitle(self):
                self.setTitle(_("Settings"))

	def initConfigList(self, element=None):
		print "[initConfigList]", element
		try:
			self.list = []
			self.list.append(getConfigListEntry(_("Show wizard on next start"), config.plugins.pvmc.showwizard))
			self.list.append(getConfigListEntry(_("Start Valerie on e2 start"),       config.plugins.pvmc.autostart))
			self.list.append(getConfigListEntry(_("Check for updates on Valerie start"),  config.plugins.pvmc.checkforupdate))
			self.list.append(getConfigListEntry(_("Backdrop quality"), config.plugins.pvmc.backdropquality))
			
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
		print "PVMC_MainMenu:__init__",isAutostart

		Screen.__init__(self, session)
		self.isAutostart = isAutostart
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		print "OLDSERVICE", self.oldService
		self.session.nav.stopService()
		#self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		#print "OLDSERVICE", self.oldService
		
		try:
			from StillPicture import StillPicture
			self["showiframe"] = StillPicture()
			self.ShowStillPicture = True
		except Exception, ex:
			print ex

		self.OldSkin = False
		try:
			if self["menuWatch"] == None:
				self.OldSkin = False
			else:
				self.OldSkin = True
		except Exception, ex:
			self.OldSkin = False

		if self.OldSkin is True:
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
		else:
			list = []
			list.append((_("Settings"), "PVMC_Settings", "menu_settings", "50"))
			list.append((_("Synchronize"),     "PVMC_Sync",     "menu_sync", "50"))
			list.append((_("Live TV"),  "InfoBar",       "menu_tv", "50"))
			list.append((_("Movies"),   "PVMC_Movies",   "menu_movies", "50"))
			list.append((_("Series"), "PVMC_Series",   "menu_series", "50"))
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

		if self.isAutostart is False and self.OldSkin is False:
			self["cancelActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.Exit,
			}, -1)
		elif self.OldSkin is True:
			self["cancelActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.cancel,
			}, -1)

		self.onFirstExecBegin.append(self.onExec)
		
		if config.plugins.pvmc.checkforupdate.value == True:
			self.onFirstExecBegin.append(self.checkForUpdate)
		
		# Executes a start script
		self.onFirstExecBegin.append(self.onExecStartScript)

	def onExec(self):
		self["menu"].setIndex(2)

	def onExecStartScript(self):
		import os
		try:
			os.system("/hdd/valerie/start.sh")
		except Exception, e:
			print "onExecStartScript failed", e

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

		if self.OldSkin is True and self.Watch == True:
			selection = self["menuWatch"].getCurrent()
			if selection is not None:
				if selection[1] == "PVMC_Movies":
					self.session.openWithCallback(self.showStillPicture, PVMC_Movies)
				elif selection[1] == "PVMC_Series":
					self.session.openWithCallback(self.showStillPicture, PVMC_Series)
		else:
			selection = self["menu"].getCurrent()
			print "SELECTION", selection
			if selection is not None:
				if selection[1] == "PVMC_Watch":
					self["menuWatch"].setIndex(2)
					self.Watch = True;
				elif selection[1] == "PVMC_Movies":
					self.session.openWithCallback(self.showStillPicture, PVMC_Movies)
				elif selection[1] == "PVMC_Series":
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
		if self.OldSkin is True:
			self.cancel()
		else:
			self["menu"].selectPrevious()
		return

	def down(self):
		if self.OldSkin is True:
			self.okbuttonClick()
		else:
			self["menu"].selectNext()
		return

	def right(self):
		if self.OldSkin is True:
			if self.Watch == True:
				self["menuWatch"].selectNext()
				if self["menuWatch"].getIndex() == 0:
					self["menuWatch"].selectNext()
			else:
				self["menu"].selectNext()

	def left(self):
		if self.OldSkin is True:
			if self.Watch == True:
				self["menuWatch"].selectPrevious()
				if self["menuWatch"].getIndex() == 0:
					self["menuWatch"].selectPrevious()
			else:
				self["menu"].selectPrevious()

	def cancel(self):
		if self.OldSkin is True:
			if self.Watch == True:
				self["menuWatch"].setIndex(0)
				self.Watch = False;

		return

	def Exit(self):
		if self.ShowStillPicture is True:
			self["showiframe"].finishStillPicture()
		print "OLDSERVICE", self.oldService
		self.session.nav.playService(self.oldService)
	
		if self.isAutostart:
			self. close()
		else:
			self.close((True,) )

