# -*- coding: utf-8 -*-

import os

from Components.config import config
from Tools.Import import my_import

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

gPlugins = []

def loadPlugins(dir, imp):
	files = []
	#go through all files and generate list
	for p in os.listdir(dir):
		files.append(p)
	#make entries unique
	files = set(files)
	
	alreadyLoaded = []
	del(alreadyLoaded[:])
	
	for f in os.listdir(dir):
		file = os.path.join(dir, f)
		if os.path.isfile(file):
			pos = f.find(".py")
			if pos > 0:
				f = f[:pos]
				#printl("f: " + str(f), __name__)
				if f in alreadyLoaded: #Dont load multiple times if py pyc and pyo exists
					continue
				try:
					m = __import__(imp + f)
					alreadyLoaded.append(f)
				except Exception, ex:
					printl("Information (" + str(type(ex)) + "): " + str(ex), __name__, "I")
					printl("\tf: " + str(f), __name__, "I")

def registerPlugin(plugin):
	#printl("name=" + str(plugin.name) + " where=" + str(plugin.where), __name__)
	ps = []
	if type(plugin) is list:
		ps = plugin
	else:
		ps.append(plugin)
	for p in ps:
		if p not in gPlugins:
			printl("registered: name=" + str(p.name) + " where=" + str(p.where), __name__)
			gPlugins.append(p)

def getPlugins(where=None):
	if where is None:
		return gPlugins
	else:
		list = []
		for plugin in gPlugins:
			if plugin.where == where:
				list.append(plugin)
		
		list.sort(key=lambda x: x.weight)
		print list
		return list

def getPlugin(name, where):
	for plugin in gPlugins:
			if plugin.name == name and plugin.where == where:
				return plugin
	return None

class Plugin():
	MENU_MAIN = 1
	MENU_PICTURES = 2
	MENU_MUSIC = 3
	MENU_VIDEOS = 4
	MENU_MOVIES = 5
	MENU_TVSHOWS = 6
	MENU_PROGRAMS = 7
	MENU_SYSTEM = 8
	
	AUTOSTART = 9
	
	SETTINGS = 10
	
	MENU_MOVIES_PLUGINS = 11
	AUTOSTART_E2 = 12
	STOP_E2 = 13
	MENU_DEV = 14
	
	WAKEUP = 15
	AUTOSTART_DELAYED = 16
	
	INFO_PLAYBACK = 100
	INFO_SEEN = 101

	name  = None
	desc = None
	start = None
	fnc   = None
	where = None
	weight = 0
	supportStillPicture = False

	def __init__(self, name=None, desc=None, start=None, fnc=None, where=None, supportStillPicture=False, weight=0):
		self.name = name
		if desc is None:
			self.desc = self.name
		else:
			self.desc = desc
		self.start = start
		self.fnc = fnc
		self.where = where
		self.weight = weight
		self.supportStillPicture = supportStillPicture
