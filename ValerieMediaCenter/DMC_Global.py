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

		environ['BOXSYSTEM'] = "MANUFACTOR=Topfield;MODEL=HDPVR-7700;"
		s = config.plugins.dmc.pluginfolderpath.value + "e2control"
		s += " &"
		printl(s)
		try:
			popen(s)
		except OSError, e: 
			printl("OSError: " + str(e))

	def close(self):
		s = "killall e2control"
		#s += " &"
		printl(s)
		try:
			popen(s)
		except OSError, e: 
			printl("OSError: " + str(e))

