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

SEENDB     = None
dbSeen     = None

imdbid      = None
thetvdb     = None
season      = None
episode     = None
status      = None
type        = None
progress    = None



def _loadSeenDB():
	global dbSeen
	global SEENDB
	printl("_loadSeenDB ->", None)
	if dbSeen is None:
		printl("_loadSeenDB loading ->", None)
		dbSeen = {}
		dbSeen["Movies"] = {}
		dbSeen["TV"] = {}
		try:
			if os.path.exists(SEENDB):
				fd = open(SEENDB, "rb")
				dbSeen = pickle.load(fd)
				fd.close()

		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60


def saveSeenDB():
	global dbSeen
	global SEENDB
	printl("saveSeenDB ->", None)
	try:		
		fd = open(SEENDB, "wb")
		pickle.dump(dbSeen, fd, pickle.HIGHEST_PROTOCOL)
		fd.close()
		
	except Exception, ex:
		print ex
		print '-'*60
		import sys, traceback
		traceback.print_exc(file=sys.stdout)
		print '-'*60

def _seenCheckLoaded():
	#log("->", self, 10)
	global dbSeen
	if dbSeen is None:
		log("SeenDB Not Loaded", None, 10)
		_loadSeenDB()

def isSeen(primary_key):
	global dbSeen
	_seenCheckLoaded()
	if primary_key.has_key("TheTvDbId"):
		try:
			return dbSeen["TV"][primary_key["TheTvDbId"]][primary_key["Season"]][primary_key["Episode"]]["Seen"]
		except Exception, ex:
			return False
	if primary_key.has_key("ImdbId"):
		try:
			return dbSeen["Movies"][primary_key["ImdbId"]]["Seen"]
		except Exception, ex:
			return False
	return False

def setSeen(primary_key):
	global dbSeen
	_seenCheckLoaded()
	if primary_key.has_key("TheTvDbId"):
		if not dbSeen["TV"].has_key(primary_key["TheTvDbId"]):
			dbSeen["TV"][primary_key["TheTvDbId"]] = {}
		if not dbSeen["TV"][primary_key["TheTvDbId"]].has_key(primary_key["Season"]):
			dbSeen["TV"][primary_key["TheTvDbId"]][primary_key["Season"]] = {}
		if not dbSeen["TV"][primary_key["TheTvDbId"]][primary_key["Season"]].has_key(primary_key["Episode"]):
			dbSeen["TV"][primary_key["TheTvDbId"]][primary_key["Season"]][primary_key["Episode"]] = {}
			
		dbSeen["TV"][primary_key["TheTvDbId"]][primary_key["Season"]][primary_key["Episode"]]["Seen"] = primary_key["Seen"]
		saveSeenDB()
		
	else:
		if primary_key.has_key("ImdbId"):
			if not dbSeen["Movies"].has_key(primary_key["ImdbId"]):
				dbSeen["Movies"][primary_key["ImdbId"]] = {}
				
			dbSeen["Movies"][primary_key["ImdbId"]]["Seen"] = primary_key["Seen"]
	return


def autostart(session):
	global dbSeen
	global SEENDB
	global imdbid
	global thetvdb
	global season
	global episode
	global status
	global type
	global progress
	SEENDB = config.plugins.pvmc.configfolderpath.value + "seen.db"
	_loadSeenDB()

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