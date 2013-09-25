# -*- coding: utf-8 -*-
'''
Project Valerie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

DreamPlex Plugin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
'''
#===============================================================================
# IMPORT
#===============================================================================
import datetime
import os
import sys
import re
import shutil

from DMC_Singleton import Singleton

from Components.config import config

#===============================================================================
# 
#===============================================================================
# we need this to work also in openPLiPc
encoding = sys.getdefaultencoding()

if encoding != "utf8":
	reload(sys)
	sys.setdefaultencoding('utf-8')
#===============================================================================
# GLOBAL
#===============================================================================
gConnectivity = None
gLogFile = None
gBoxType = None

STARTING_MESSAGE	= ">>>>>>>>>>"
CLOSING_MESSAGE		= "<<<<<<<<<<"
#===============================================================================
# 
#===============================================================================
def printl2 (string, parent=None, dmode= "U", obfuscate = False, steps = 4):
	'''
	@param string: 
	@param parent:
	@param dmode: default = "U" undefined 
							"E" shows error
							"W" shows warning
							"I" shows important information to have better overview if something really happening or not
							"D" shows additional debug information for better debugging
							"S" shows started functions/classes etc.
							"C" shows closing functions/classes etc.
	@return: none
	'''

	debugMode = config.plugins.pvmc.debugMode.value
	
	if debugMode:
		
		out = ""
		if obfuscate is True:
			string = string[:-steps]
			for i in range(steps):
				string += "*"
			
		if parent is None:
			out = str(string)
		else:
			classname = str(parent.__class__).rsplit(".", 1)
			if len(classname) == 2:
				classname = classname[1]
				classname = classname.rstrip("\'>")
				classname += "::"
				out = str(classname) + str(sys._getframe(1).f_code.co_name) +" -> " + str(string)
			else:
				classname = ""
				out = str(parent) + " -> " + str(string)
	
		if dmode == "E" :
			print "[PVMC] " + "E" + "  " + str(out)
			writeToLog(dmode, out)
		
		elif dmode == "W":
			print "[PVMC] " + "W" + "  " + str(out)
			writeToLog(dmode, out)
		
		elif dmode == "I":
			print "[PVMC] " + "I" + "  " + str(out)
			writeToLog(dmode, out)
		
		elif dmode == "D":
			print "[PVMC] " + "D" + "  " + str(out)	
			writeToLog(dmode, out)
		
		elif dmode == "S":
			print "[PVMC] " + "S" + "  " + str(out) + STARTING_MESSAGE
			writeToLog(dmode, out + STARTING_MESSAGE)
		
		elif dmode == "C":
			print "[PVMC] " + "C" + "  " + str(out) +  CLOSING_MESSAGE
			writeToLog(dmode, out +  CLOSING_MESSAGE)
		
		elif dmode == "U":
			print "[PVMC] " + "UNKNOWN" + "  " + str(out)
			writeToLog(dmode, out)
			
		elif dmode == "X":
			print "[PVMC] " + "D" + "  " + str(out)	
			writeToLog(dmode, out)
			
		else:
			print "[PVMC] " + "OLD CHARACTER CHANGE ME !!!!!" + "  " + str(out)

#===============================================================================
# 
#===============================================================================
def printl2cond (cond, string, parent=None, verbLevel=None):
	'''
	is used for xml - very chatty - we should get rid off it
	'''
	#printl2("", "__common__::printl2cond", "S")
	
	if cond:
		printl2(string, parent)
	
	#printl2("", "__common__::printl2cond", "C")
		
#===============================================================================
# 
#===============================================================================
def writeToLog(dmode, out):
	'''
	singleton handler for the log file
	
	@param dmode: E, W, S, H, A, C, I
	@param out: message string
	@return: none
	'''
	try:
		instance = Singleton()
		if instance.getLogFileInstance() is "":
			openLogFile()
			gLogFile = instance.getLogFileInstance()
			gLogFile.truncate()
		else:
			gLogFile = instance.getLogFileInstance()
			
		now = datetime.datetime.now()
		gLogFile.write("%02d:%02d:%02d.%07d " % (now.hour, now.minute, now.second, now.microsecond) + " >>> " + str(dmode) + " <<<  " + str(out) + "\n")
		gLogFile.flush()
	
	except Exception, ex:
		printl2("Exception(" + str(type(ex)) + "): " + str(ex), "__common__::writeToLog", "E")

#===============================================================================
# 
#===============================================================================
def openLogFile():
	'''
	singleton instance for logfile
	
	@param: none
	@return: none
	'''
	#printl2("", "openLogFile", "S")
	
	baseDir = config.plugins.pvmc.tmpfolderpath.value
	logDir = baseDir + "/log"
	
	now = datetime.datetime.now()
	try:
		if os.path.exists(logDir + "valerie_former.log"):
			os.remove(logDir + "valerie_former.log")
			
		if os.path.exists(logDir + "valerie.log"):
			shutil.copy2(logDir + "valerie.log", logDir + "valerie_former.log")
		
		instance = Singleton()
		instance.getLogFileInstance(open(logDir + "valerie.log", "w"))
		
	except Exception, ex:
		printl2("Exception(" + str(type(ex)) + "): " + str(ex), "openLogFile", "E")
	
	#printl2("", "openLogFile", "C")

#===============================================================================
# 
#===============================================================================
def isInetAvailable():
	printl2("", "__common__::isInetAvailable", "S")
	
	global gConnectivity
	if gConnectivity is None:
		gConnectivity = testInetConnectivity()
	
	printl2("", "__common__::isInetAvailable", "C")
	return gConnectivity

#===============================================================================
# 
#===============================================================================
def testInetConnectivity(target = "http://www.google.com"):
	'''
	test if we get an answer from the specified url
	
	@param url:
	@return: bool
	'''
	printl2("", "__common__::testInetConnectivity", "S")
	
	import urllib2
	from   sys import version_info
	import socket
	
	try:
		opener = urllib2.build_opener()
		page = None
		if version_info[1] >= 6:
			page = opener.open(target, timeout=2)
		else:
			socket.setdefaulttimeout(2)
			page = opener.open(target)
		if page is not None:
			
			printl2("","__common__::testInetConnectivity", "C")
			return True
		else:
			
			printl2("","__common__::testInetConnectivity", "C")
			return False
	except:
		
		printl2("", "__common__::testInetConnectivity", "C")
		return False

#===============================================================================
# 
#===============================================================================
def checkValerieEnvironment(): # TODO implement me
	'''
	checks needed file structure for valerie
	
	@param: none 
	@return none	
	'''
	printl2("","__common__::checkPlexEnvironment", "S")
	
	playerTempFolder = config.plugins.pvmc.playerTempPath.value
	logFolder = config.plugins.pvmc.logfolderpath.value
	mediaFolder = config.plugins.pvmc.mediafolderpath.value
	configFolder = config.plugins.pvmc.configfolderpath.value
	
	checkDirectory(playerTempFolder)
	checkDirectory(logFolder)
	checkDirectory(mediaFolder)
	checkDirectory(configFolder)
	
	printl2("","__common__::checkPlexEnvironment", "C")
	
#===============================================================================
# 
#===============================================================================
def checkDirectory(directory):
	'''
	checks if dir exists. if not it is added
	
	@param directory: e.g. /media/hdd/
	@return: none
	'''
	printl2("", "__common__::checkDirectory", "S")
	printl2("checking ... " + directory, "__common__::checkDirectory", "D")
	
	try:
		if not os.path.exists(directory):
			os.makedirs(directory)
			printl2("directory not found ... added", "__common__::checkDirectory", "D")
		else:
			printl2("directory found ... nothing to do", "__common__::checkDirectory", "D")
		
	except Exception, ex:
		printl2("Exception(" + str(type(ex)) + "): " + str(ex), "__common__::checkDirectory", "E")
	
	printl2("","__common__::checkDirectory", "C")

#===============================================================================
# 
#===============================================================================
def getBoxtype():
	'''
	'''
	printl2("", "__common__::getBoxtype", "C")
	global gBoxType

	if gBoxType is not None:
		
		printl2("", "__common__::getBoxtype", "C")
		return gBoxType
	else:
		setBoxType()
		
		printl2("", "__common__::getBoxtype", "C")
		return gBoxType

#===============================================================================
# 
#===============================================================================
def setBoxType():
	'''
	'''
	printl2("", "__common__::_setBoxtype", "C")
	global gBoxType
	
	try:
		file = open("/proc/stb/info/model", "r")
	except:
		file = open("/hdd/model", "r")
	box = file.readline().strip()
	file.close()
	manu = "Unknown"
	model = box #"UNKNOWN" # Fallback to internal string
	arch = "sh4" # "unk" # Its better so set the arch by default to unkown so no wrong update information will be displayed
	version = ""
	if box == "ufs910":
		manu = "Kathrein"
		model = "UFS-910"
		arch = "sh4"
	elif box == "ufs912":
		manu = "Kathrein"
		model = "UFS-912"
		arch = "sh4"
	elif box == "ufs922":
		manu = "Kathrein"
		model = "UFS-922"
		arch = "sh4"
	elif box == "tf7700hdpvr":
		manu = "Topfield"
		model = "HDPVR-7700"
		arch = "sh4"
	elif box == "dm800":
		manu = "Dreambox"
		model = "800"
		arch = "mipsel"
	elif box == "dm800se":
		manu = "Dreambox"
		model = "800se"
		arch = "mipsel"
	elif box == "dm8000":
		manu = "Dreambox"
		model = "8000"
		arch = "mipsel"
	elif box == "dm500hd":
		manu = "Dreambox"
		model = "500hd"
		arch = "mipsel" 
	elif box == "dm7025":
		manu = "Dreambox" 
		model = "7025"
		arch = "mipsel"  
	elif box == "dm7020hd":
		manu = "Dreambox"
		model = "7020hd"
		arch = "mipsel"
	elif box == "elite":
		manu = "Azbox"
		model = "Elite"
		arch = "mipsel"
	elif box == "premium":
		manu = "Azbox"
		model = "Premium"
		arch = "mipsel"
	elif box == "premium+":
		manu = "Azbox"
		model = "Premium+"
		arch = "mipsel"
	elif box == "cuberevo-mini":
		manu = "Cubarevo"
		model = "Mini"
		arch = "sh4"
	elif box == "hdbox":
		manu = "Fortis"
		model = "HdBox"
		arch = "sh4"
	
	if arch == "mipsel":
		version = getBoxArch()
	else:
		version = "duckbox"
	
	gBoxType = (manu, model, arch, version)
	printl2("", "__common__::_setBoxtype", "C")

#===============================================================================
# 
#===============================================================================
def getBoxArch():
	'''
	'''
	printl2("", "__common__::getBoxArch", "S")
	
	ARCH = "unknown"

	if (sys.version_info < (2, 6, 8) and sys.version_info > (2, 6, 6)):
		ARCH = "oe16"
				   
	if (sys.version_info < (2, 7, 4) and sys.version_info > (2, 7, 0)):
		ARCH = "oe20"
			
	printl2("", "__common__::getBoxArch", "C")
	return ARCH

#===============================================================================
# 
#===============================================================================
def resub(pattern, replacement, input):
	'''
	Wrapper to create a real global re.sub function
	'''
	printl2("", "__common__::resub", "S")
	
	output = ""
	tmpinput = input
	
	while True:
		output = re.sub(pattern, replacement, tmpinput)
		if output == tmpinput:
			break
		tmpinput = output
	
	printl2("", "__common__::resub", "C")
	return output
