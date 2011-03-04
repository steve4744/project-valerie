# -*- coding: utf-8 -*-

import datetime
import os
import sys

#------------------------------------------------------------------------------------------

gLogFile = None
#gLogFileHtml = None

def openLogFile():
	global gLogFile
#	global gLogFileHtml
	now = datetime.datetime.now()
	gLogFile = open("/tmp/valerie_%04d%02d%02d_%02d%02d.log" % (now.year, now.month, now.day, now.hour, now.minute, ), "w")
	#gLogFileHtml = open("/tmp/valerie_%04d%02d%02d_%02d%02d.html" % (now.year, now.month, now.day, now.hour, now.minute, ), "w")

def printl2(string, parent=None):
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
	print "[Valerie] " + str(out)
	now = datetime.datetime.now()
	gLogFile.write("%02d:%02d " % (now.hour, now.minute, ) + str(out) + "\n")
	#gLogFileHtml.write("%02d:%02d " % (now.hour, now.minute, ) + str(out) + "<br />")
	gLogFile.flush()
	#gLogFileHtml.flush()
