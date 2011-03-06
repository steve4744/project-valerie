# -*- coding: utf-8 -*-

import os

from Components.config import config
from Tools.Import import my_import

gPlugins = []

def loadPlugins(dir, imp):
	for f in os.listdir(dir):
		file = os.path.join(dir, f)
		if os.path.isfile(file):
			pos = f.find(".py")
			if pos > 0:
				#print f
				f = f[:pos]
				if f == "__init__":
					continue
				try:
					m = __import__(imp + f)
				except Exception, ex:
					print "Exception:", ex

def registerPlugin(plugin):
	ps = []
	if type(plugin) is list:
		ps = plugin
	else:
		ps.append(plugin)
	for p in ps:
		if p not in gPlugins:
			gPlugins.append(p)

def getPlugins(where=None):
	if where is None:
		return gPlugins
	else:
		list = []
		for plugin in gPlugins:
			if plugin.where == where:
				list.append(plugin)
		return list

class Plugin():

	MENU_MAIN = 1
	MENU_PICTURES = 2
	MENU_MUSIC = 3
	MENU_VIDEOS = 4
	MENU_MOVIES = 5
	MENU_TVSHOWS = 6
	MENU_PROGRAMS = 7
	MENU_SYSTEM = 8

	name = None
	start = None
	fnc = None
	where = None
	supportStillPicture = False

	def __init__(self, name=None, start=None, fnc=None, where=None, supportStillPicture=False):
		self.name = name
		self.start = start
		self.fnc = fnc
		self.where = where
		self.supportStillPicture = supportStillPicture
