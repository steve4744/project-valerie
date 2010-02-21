from Components.config import config
from _ctypes import *
from os import environ, popen, makedirs

class Showiframe():
	def __init__(self):
		self.showiframe = dlopen(config.plugins.dmc.pluginfolderpath.value + "libshowiframe.so.0.0.0")
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
		# TODO: Change dinaicaly
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

		file = open("/proc/stb/info/model", "r")
		box = file.readline().strip()
		file.close()
		manu = "Unknown"
		model = "UNKNOWN"
		if box == "ufs910":
			manu = "Kathrein"
			model = "UFS-910"
		elif box == "ufs912":
			manu = "Kathrein"
			model = "UFS-912"
		elif box == "ufs922":
			manu = "Kathrein"
			model = "UFS-922"
		elif box == "tf7700hdpvr":
			manu = "Topfield"
			model = "HDPVR-7700"
		elif box == "dm800":
			manu = "Dreambox"
			model = "800"
		elif box == "dm8000":
			manu = "Dreambox"
			model = "8000"
		environ['BOXSYSTEM'] = "MANUFACTOR="+manu+";MODEL="+model+";"
		s = config.plugins.dmc.pluginfolderpath.value + " e2control"
		printl(s)
		try:
			popen(s)
		except OSError, e: 
			printl("OSError: " + str(e))

	def close(self):
		s = config.plugins.dmc.pluginfolderpath.value + " e2control stop"
		printl(s)
		try:
			popen(s)
		except OSError, e: 
			printl("OSError: " + str(e))

