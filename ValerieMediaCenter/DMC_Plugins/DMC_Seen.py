# -*- coding: utf-8 -*-

from Components.config import config
from Components.config import ConfigPassword
from Components.config import ConfigSubsection
from Components.config import ConfigText
from Components.config import ConfigYesNo

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin
import cPickle   as pickle

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

gAvailable = False
try:
	gAvailable = True
except:
	gAvailable = False

progress    = None
status      = None
manager     = None

def setSeen(id, seen):
	global manager
	if manager is None:
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		manager = Manager("DMC_SEEN")
	if seen:
	#	manager.MarkAsSeen(id, None)
		manager.MarkAsSeen(id)
	else:
		manager.MarkAsUnseen(id)
	
def autostart(session):
	global progress
	global status
	global manager
		
def markSeen(session, args):
	if args.has_key("Id"):
		setSeen(args["Id"], True)
	
def markUnSeen(session, args):
	if args.has_key("Id"):
		setSeen(args["Id"], False)
	
def info_playback(d, flags):
	global progress
	global status
	if flags.has_key("DO_NOT_TRACK") and flags["DO_NOT_TRACK"] is True:
		return
	
	status = ""
	if d.has_key("progress"):
		progress = d["progress"]
	if d.has_key("status"):
		status = d["status"]

	if status == "stopped":
		if progress >= 70:
			pass;
			#setSeen(d["Id"], True)

if gAvailable is True:
	registerPlugin(Plugin(name=_("Seen"), fnc=autostart, where=Plugin.AUTOSTART))
	registerPlugin(Plugin(name=_("Seen"), fnc=info_playback, where=Plugin.INFO_PLAYBACK))
	#registerPlugin(Plugin(name=_("Seen"), fnc=is_Seen, where=Plugin.INFO_SEEN))
	registerPlugin(Plugin(name=_("Mark as Seen"), fnc=markSeen, where=Plugin.MENU_MOVIES_PLUGINS))
	registerPlugin(Plugin(name=_("Mark as Unseen"), fnc=markUnSeen, where=Plugin.MENU_MOVIES_PLUGINS))