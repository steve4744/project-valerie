# -*- coding: utf-8 -*-

from os import makedirs, environ, popen, system
import sys
import traceback

from Components.config import config

from DataElement import DataElement

#------------------------------------------------------------------------------------------

def getAPILevel(parent):
	APILevel = 1
	try:
		APILevel = int(DataElement().getDataPreloading(parent, "API"))
	except Exception, ex:
		printl(str(ex))
		APILevel = 1
	return APILevel

#------------------------------------------------------------------------------------------

def getBoxtype():
	file = open("/proc/stb/info/model", "r")
	box = file.readline().strip()
	file.close()
	manu = "Unknown"
	model = box #"UNKNOWN" # Fallback to internal string
	arch = "sh4" # "unk" # Its better so set the arch by default to unkown so no wrong updateinformation will be displayed
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
		file = open(config.plugins.pvmc.pluginfolderpath.value + "oe.txt", "r")
		version = file.readline().strip()
		file.close()
		
	return (manu, model, arch, version)
	
#------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------

class Showiframe():
	def __init__(self):
		try:
			self.load()
		except Exception, ctypeEx: 
			print "ARRRGH!! SHOWIFRAME FAILED", ctypeEx
			

	def load(self):
		sys.path.append(config.plugins.pvmc.pluginfolderpath.value + "prebuild")
		print "SYS.PATH", sys.path
		try:
			self.ctypes = __import__("_ctypes")
		except Exception, e:
			print "self.ctypes import failed", e
			self.ctypes = None
			return False
		
		libname = "libshowiframe.so.0.0.0"
		if getBoxtype()[0] == "Azbox":
			libname = "libshowiframe.az.so.0.0.0"
		
		print "LIB_PATH:", config.plugins.pvmc.pluginfolderpath.value + libname
		self.showiframe = self.ctypes.dlopen(config.plugins.pvmc.pluginfolderpath.value + libname)
		try:
			self.showSinglePic = self.ctypes.dlsym(self.showiframe, "showSinglePic")
			self.finishShowSinglePic = self.ctypes.dlsym(self.showiframe, "finishShowSinglePic")
		except Exception, e: 
			print "self.ctypes.dlsym - FAILED!!!", e
			try:
				self.showSinglePic = self.ctypes.dlsym(self.showiframe, "_Z13showSinglePicPKc")
				self.finishShowSinglePic = self.ctypes.dlsym(self.showiframe, "_Z19finishShowSinglePicv")
			except Exception, e2: 
				print "self.ctypes.dlsym - FAILED AGAIN !!!", e2
				return False
		return True

	def  showStillpicture(self, pic):
		if self.ctypes is not None:
			self.ctypes.call_function(self.showSinglePic, (pic, ))

	def finishStillPicture(self):
		if self.ctypes is not None:
			self.ctypes.call_function(self.finishShowSinglePic, ())
			#dlclose(self.showiframe)

def printl(string):
	print "[Project Valerie] ", string

#------------------------------------------------------------------------------------------

class E2Control():
	def __init__(self):
		printl("E2Control::__init__ ->")
		
		try:
			makedirs("/hdd/valerie")
		except OSError, e: 
			printl("OSError: " + str(e))
		try:
			makedirs("/hdd/valerie/episodes")
		except OSError, e: 
			printl("OSError: " + str(e))
		try:
			makedirs("/hdd/valerie/media")
		except OSError, e: 
			printl("OSError: " + str(e))
		
		self.close()
		
		box = getBoxtype()
		environ['BOXSYSTEM'] = "MANUFACTOR="+box[0]+";MODEL="+box[1]+";"
		s = config.plugins.pvmc.pluginfolderpath.value + "e2control"
		printl(s)
		try:
			import os
			system("chmod 777 " + s)
			popen(s)
		except OSError, e: 
			printl("OSError: " + str(e))
		
		printl("E2Control::__init__ <-")

	def close(self):
		printl("E2Control::close ->")
		s = config.plugins.pvmc.pluginfolderpath.value + "e2control stop"
		printl(s)
		try:
			popen(s)
		except OSError, e: 
			printl("OSError: " + str(e))
		printl("E2Control::close <-")

