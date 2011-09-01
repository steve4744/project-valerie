# -*- coding: utf-8 -*-

from threading import Thread

from Components.config import config
from Components.config import ConfigYesNo
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

from Components.Language import language
import gettext
import os
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE

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

gAvailable = True

config.plugins.pvmc.plugins.backgrounddbloader = ConfigSubsection()
config.plugins.pvmc.plugins.backgrounddbloader.autoload = ConfigYesNo(default = True)

class BackgroundDbLoader(Thread):
	def run(self):
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		m = Manager()

def autostart(session):
	try:
		thread = BackgroundDbLoader()
		thread.start()
	except Exception, ex:
		printl("Exception(Can be ignored): " + str(ex), __name__, "W")

def settings():
	s = []
	s.append((_("Autoload Database on start"), config.plugins.pvmc.plugins.backgrounddbloader.autoload, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(name=_("BackgroundDbLoader"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(name=_("BackgroundDbLoader"), fnc=autostart, where=Plugin.AUTOSTART))