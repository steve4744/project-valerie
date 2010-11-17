from Components.config import config

from os import environ, popen, makedirs
from sys import version_info
import sys, traceback

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------

def getBoxtype():
	file = open("/proc/stb/info/model", "r")
	box = file.readline().strip()
	file.close()
	manu = "Unknown"
	model = box #"UNKNOWN" # Fallback to internal string
	arch = "unk" # Its better so set the arch by default to unkown so no wrong updateinformation will be displayed
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
	
	if arch == "mipsel":
		file = open(config.plugins.pvmc.pluginfolderpath.value + "oe.txt", "r")
		version = file.readline().strip()
		file.close()
		
	return (manu, model, arch, version)
	
#------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------

try:
	from _ctypes import *
except Exception, e: 
	import urllib2
	try:
	
		box = getBoxtype()
		dir = ""
		#url = "http://duckbox.info/valerie/prebuilt/" + box[2]
		#url += "/_ctypes.so"
		if box[3] == "oe15":
			#url += ".25"
			dir += "/usr/lib/python2.5/lib-dynload/"
		elif box[3] == "oe16":
			#url += ".26"
			dir += "/usr/lib/python2.6/lib-dynload/"
		else:
			dir += "/usr/lib/python2.6/lib-dynload/"
		
		print "URL: " + url
		#page = urllib2.urlopen(url)
		page = open(config.plugins.pvmc.pluginfolderpath.value + "prebuild/_ctypes.so", 'rb')
		
		f = open(dir + "_ctypes.so", 'wb')
		f.write(page.read())
		f.close()
	except Exception, ex:
		print "File download failed: ", ex
		print type(ex)
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60

from _ctypes import *

#------------------------------------------------------------------------------------------

class Showiframe():
	def __init__(self):
		self.showiframe = dlopen(config.plugins.pvmc.pluginfolderpath.value + "libshowiframe.so.0.0.0")
		try:
			self.showSinglePic = dlsym(self.showiframe, "showSinglePic")
			self.finishShowSinglePic = dlsym(self.showiframe, "finishShowSinglePic")
		except OSError, e: 
			self.showSinglePic = dlsym(self.showiframe, "_Z13showSinglePicPKc")
			self.finishShowSinglePic = dlsym(self.showiframe, "_Z19finishShowSinglePicv")

	def  showStillpicture(self, pic):
		call_function(self.showSinglePic, (pic, ))

	def finishStillPicture(self):
		call_function(self.finishShowSinglePic, ())
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

