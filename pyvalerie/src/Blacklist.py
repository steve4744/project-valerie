# -*- coding: utf-8 -*-

from Components.config import config

import Utf8

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

blackList = []

def load():
	del blackList[:]
	fconf = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + "blacklist.conf", "r")
	blackList = fconf.read().split(u"\n")
	fconf.close()

def save():
	fconf = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + "blacklist.conf", "w")
	for file in blackList:
		fconf.write(file + u"\n")
	fconf.close()

def get():
	return blackList

def add(filename):
	blackList.append(filename)
