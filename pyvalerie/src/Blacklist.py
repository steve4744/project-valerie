# -*- coding: utf-8 -*-

from Components.config import config

import Utf8

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

blackList = []

def load():
	global blackList
	printl("loading blackList")
	try:
		del blackList[:]
		fconf = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + "blacklist.conf", "r")
		blackList = fconf.read().split(u"\n")
		printl("blacklist loaded " + str(len(blackList))+ " entries")
		fconf.close()
	except Exception, ex:
		printl("blacklist not found")
		blackList = []
		
	
def save():
	global blackList
	if blackList is None:
		self.load()
		
	fconf = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + "blacklist.conf", "w")
	for file in blackList:
		fconf.write(file + u"\n")
	fconf.close()

def get():
	global blackList
	if blackList is None:
		self.load()
	return blackList

def add(filename):
	global blackList
	if blackList is None:
		self.load()
	blackList.append(filename)
