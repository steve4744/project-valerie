# -*- coding: utf-8 -*-

import datetime
import os
import sys

from   Components.config import config

#------------------------------------------------------------------------------------------

gLogFile = None

# ****************************** VERBOSITY Level *******************************
# 	unspecified level will be DEBUG_INFO level 20
#
VERB_TOLOG   = 21 # (10??) pass to User Configuration
VERB_DEFAULT = 20 
VERB_ENTERFUNCTION  =  10
VERB_ENTERFUNCTION2 =  15  # for functions with lot off calls
#  give console warning (yellow) at level <= 10
VERB_WARNING =  3
#  give console error (red) at level <= 1
VERB_ERROR   =  2
#  not implemented - Alert User
VERB_ERROR_NOTIFYUSER = 1

def openLogFile():
	global gLogFile
	baseDir = config.plugins.pvmc.tmpfolderpath.value
	logDir = baseDir + "/log"
	
	now = datetime.datetime.now()
	
	try: 
		os.makedirs(baseDir)
	except OSError, e:
		pass
	
	try: 
		os.makedirs(logDir)
	except OSError, e:
		pass
	
	gLogFile = open(logDir + "/valerie_%04d%02d%02d_%02d%02d.log" % (now.year, now.month, now.day, now.hour, now.minute, ), "w")
	#gLogFileHtml = open("/tmp/valerie_%04d%02d%02d_%02d%02d.html" % (now.year, now.month, now.day, now.hour, now.minute, ), "w")

def printl2(string, parent=None, type="I"):
	global gLogFile
	#global gLogFileHtml
	if gLogFile is None:
		openLogFile()
		
	out = ""
	if parent is None:
		out = str(string)
	else:
		classname = str(parent.__class__).rsplit(".", 1)
		if len(classname) == 2:
			classname = classname[1]
			classname = classname.rstrip("\'>")
			classname += "::"
			
		else:
			classname = ""
		out = str(classname) + str(sys._getframe(1).f_code.co_name) +" " + str(string)
	if type == "E":
		print '\033[1;41m' + "[Valerie] " + str(type) + "  " + str(out) + '\033[1;m'
	elif type == "W":
		print '\033[1;33m' + "[Valerie] " + str(type) + "  " + str(out) + '\033[1;m'
	elif type == "S":
		print '\033[1;32m' + "[Valerie] " + str(type) + "  " + str(out) + '\033[1;m'
	elif type == "D":
		print '\033[1;21m' + "[Valerie] " + str(type) + "  " + str(out) + '\033[1;m'	
	else:
		print "[Valerie] " + str(type) + "  " + str(out)
	now = datetime.datetime.now()
	gLogFile.write("%02d:%02d:%02d.%07d " % (now.hour, now.minute, now.second, now.microsecond) + str(type) + "  " + str(out) + "\n")
	gLogFile.flush()
	#gLogFileHtml.flush()


def log (string, parent=None, verbLevel=VERB_DEFAULT):
	out = ""
	if parent is None:
		out = str(string)
	else:
		classname = str(parent.__class__).rsplit(".", 1)
		if len(classname) == 2:
			classname = classname[1]
			classname = classname.rstrip("\'>")
			classname += "::"
			
		else:
			classname = ""
		out = str(classname) + str(sys._getframe(1).f_code.co_name) +" " + str(string)

	if verbLevel == VERB_ERROR:
		printl2 (str(out), None, "E")
	elif verbLevel == VERB_WARNING:
		printl2 (str(out), None, "W")
	elif verbLevel == 99: # "S" Success ???
		printl2 (str(out), None, "S")
	elif verbLevel <= VERB_TOLOG:
		printl2 (str(out), None)
	