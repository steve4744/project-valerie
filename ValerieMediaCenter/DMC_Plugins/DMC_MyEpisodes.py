# -*- coding: utf-8 -*-

from Components.config import config
from Components.config import ConfigPassword
from Components.config import ConfigSubsection
from Components.config import ConfigText
from Components.config import ConfigYesNo

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

gAvailable = False
try:
	from MyEpisodesAPI import MyEpisodesAPI 
	gAvailable = True
except:
	gAvailable = False

config.plugins.pvmc.plugins.myepisodes          = ConfigSubsection()
config.plugins.pvmc.plugins.myepisodes.enabled  = ConfigYesNo(default = False)
config.plugins.pvmc.plugins.myepisodes.username = ConfigText(default = "No Username")
config.plugins.pvmc.plugins.myepisodes.password = ConfigPassword(default = "No Password")

def settings():
	s = []
	s.append((_("Enabled"),  config.plugins.pvmc.plugins.myepisodes.enabled, ))
	s.append((_("Username"), config.plugins.pvmc.plugins.myepisodes.username, ))
	s.append((_("Password"), config.plugins.pvmc.plugins.myepisodes.password, ))
	return s

gmy = None

def autostart(session):
	global gmy
	gmy = MyEpisodesAPI()

def info_playback(d):
	if d.has_key("title"):
		gmy.setName(d["title"])
	if d.has_key("season") and d.has_key("episode"):
		gmy.setSeasonAndEpisode(d["season"], d["episode"])
	if d.has_key("type"):
		if d["type"] == "tvshow":
			gmy.setType(MyEpisodesAPI.TYPE_TVSHOW)
		else:
			gmy.setType(-1)
	if d.has_key("progress"):
		gmy.setProgress(d["progress"])
	
	if config.plugins.pvmc.plugins.myepisodes.enabled.value is True:
		gmy.setUsernameAndPassword(config.plugins.pvmc.plugins.myepisodes.username.value, config.plugins.pvmc.plugins.myepisodes.password.value)
		if gmy.getType() == MyEpisodesAPI.TYPE_TVSHOW:
			if d.has_key("status"):
				if d["status"] == "stopped":
					if gmy.getProgress() >= 70:
						gmy.send()

if gAvailable is True:
	registerPlugin(Plugin(name=_("myepisodes"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(name=_("myepisodes"), fnc=autostart, where=Plugin.AUTOSTART))
	registerPlugin(Plugin(name=_("myepisodes"), fnc=info_playback, where=Plugin.INFO_PLAYBACK))