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

imdbid      = None
thetvdb     = None
season      = None
episode     = None
status      = None
type        = None
progress    = None
manager     = None

def isSeen(primary_key):
	global manager
	if manager is None:
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		manager = Manager("DMC_SEEN")	
	return manager.isSeenDB(primary_key)

def setSeen(primary_key):
	global manager
	if manager is None:
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		manager = Manager("DMC_SEEN")	
	manager.setSeen(primary_key)

def autostart(session):
	global imdbid
	global thetvdb
	global season
	global episode
	global status
	global type
	global progress
	global manager
		
def markSeen(session, args):
	if args.has_key("TheTvDbId"):
		if args.has_key("Season"):
			if args.has_key("Episode"):
				setSeen({"TheTvDbId": args["TheTvDbId"], "Episode":args["Episode"], "Season": args["Season"], "Seen": True})
	else:
		if args.has_key("ImdbId"):
			setSeen({"ImdbId": args["ImdbId"],  "Seen": True})
	return

	
def markUnSeen(session, args):
	if args.has_key("TheTvDbId"):
		if args.has_key("Season"):
			if args.has_key("Episode"):
				setSeen({"TheTvDbId": args["TheTvDbId"], "Episode":args["Episode"], "Season": args["Season"], "Seen": False})
	else:
		if args.has_key("ImdbId"):
			setSeen({"ImdbId": args["ImdbId"],  "Seen": False})
	return
	
def info_playback(d, flags):
	global imdbid
	global thetvdb
	global season
	global episode
	global status
	global type
	global progress
	if flags.has_key("DO_NOT_TRACK") and flags["DO_NOT_TRACK"] is True:
		return
	
	if d.has_key("imdbid"):
		imdbid = d["imdbid"]
	if d.has_key("thetvdb"):
		thetvdb = d["thetvdb"]
	if d.has_key("season") and d.has_key("episode"):
		season = d["season"]
		episode = d["episode"]
	if d.has_key("status"):
		status = d["status"]
	if d.has_key("type"):
		type = d["type"]
	if d.has_key("progress"):
		progress = d["progress"]
	
	if status == "stopped":
		if progress >= 70:
			if type == "movie":
				setSeen({"ImdbId": imdbid, "Seen": True})
			elif type == "tvshow":
				setSeen({"TheTvDbId": thetvdb, "Episode":episode, "Season": season, "Seen": True})
				

if gAvailable is True:
	registerPlugin(Plugin(name=_("Seen"), fnc=autostart, where=Plugin.AUTOSTART))
	registerPlugin(Plugin(name=_("Seen"), fnc=info_playback, where=Plugin.INFO_PLAYBACK))
	registerPlugin(Plugin(name=_("Seen"), fnc=isSeen, where=Plugin.INFO_SEEN))
	registerPlugin(Plugin(name=_("Mark as Seen"), fnc=markSeen, where=Plugin.MENU_MOVIES_PLUGINS))
	registerPlugin(Plugin(name=_("Mark as Unseen"), fnc=markUnSeen, where=Plugin.MENU_MOVIES_PLUGINS))