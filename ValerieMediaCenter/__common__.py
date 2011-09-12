# -*- coding: utf-8 -*-
import datetime
import os
import sys

from   Components.config import config
#------------------------------------------------------------------------------------------

gLogFile = None

#########################################
#Black       0;30     Dark Gray     1;30#
#Blue        0;34     Light Blue    1;34#
#Green       0;32     Light Green   1;32#
#Cyan        0;36     Light Cyan    1;36#
#Red         0;31     Light Red     1;31#
#Purple      0;35     Light Purple  1;35#
#Brown       0;33     Yellow        1;33#
#Light Gray  0;37     White         1;37#
#########################################

# ****************************** VERBOSITY Level *******************************
VERB_ERROR       = 1  # "E" shows error
VERB_WARNING     = 2  # "W" shows warning
VERB_STARTING    = 3  # "S" shows started functions/classes etc.
VERB_HIGHLIGHT   = 4  # "H" shows important hightlights to have better overview if somehtings really happening or not
VERB_DEFAULT     = 10 # "I" default verbose level when not specified
VERB_TOLOG       = 20 # " " max verbose level that shows up in normal log

##
# 
##
def printl2 (string, parent=None, verbLevel=VERB_DEFAULT):
	type = "I"
	
	if verbLevel == "E":
		verbLevel = 1
		type = "E"
	
	elif verbLevel == "W":
		verbLevel = 2
		type = "W"
	
	elif verbLevel == "S":
		verbLevel = 3
		type = "S"
	
	elif verbLevel == "H":
		verbLevel = 4
		type = "H"
	
	elif verbLevel == "I":
		verbLevel = 10
		type = "I"
		
	out = ""
	if parent is None:
		out = str(string)
	else:
		classname = str(parent.__class__).rsplit(".", 1)
		if len(classname) == 2:
			classname = classname[1]
			classname = classname.rstrip("\'>")
			classname += "::"
			out = str(classname) + str(sys._getframe(1).f_code.co_name) +" " + str(string)
		else:
			classname = ""
			out = str(parent) + str(string)

	if verbLevel == VERB_ERROR:
		print '\033[1;41m' + "[PVMC] " + "E" + "  " + str(out) + '\033[1;m'
		writeToLog(type, out)
	
	elif verbLevel == VERB_WARNING:
		print '\033[1;33m' + "[PVMC] " + "W" + "  " + str(out) + '\033[1;m'
		writeToLog(type, out)
	
	elif verbLevel == VERB_STARTING:
		print '\033[1;32m' + "[PVMC] " + "S" + "  " + str(out) + '\033[1;m'
		writeToLog(type, out)
	
	elif verbLevel == VERB_HIGHLIGHT:
		print '\033[1;35m' + "[PVMC] " + "H" + "  " + str(out) + '\033[1;m'	
		writeToLog(type, out)
	
	elif verbLevel <= VERB_TOLOG:
		print '\033[0;36m' + "[PVMC] " + "I" + "  " + '\033[1;m' + str(out) 
		writeToLog(type, out)
	
	elif verbLevel > VERB_TOLOG:
		print '\033[0;36m' + "[PVMC] " + "only onScreen" + "  " + str(out) + '\033[1;m'

		
def writeToLog(type, out):
	global gLogFile

	if gLogFile is None:
		openLogFile()
		
	now = datetime.datetime.now()
	gLogFile.write("%02d:%02d:%02d.%07d " % (now.hour, now.minute, now.second, now.microsecond) + str(type) + "  " + str(out) + "\n")
	gLogFile.flush()	

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
	