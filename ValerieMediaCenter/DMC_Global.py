from Components.config import config
from _ctypes import *
from os import environ, popen

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
		environ['BOXSYSTEM'] = "MANUFACTOR=Topfield;MODEL=HDPVR-7700;"
		s = config.plugins.dmc.pluginfolderpath.value + "e2control"
		s += " &"
		print s
		try:
			popen(s)
		except OSError, e: 
			printl("OSError: " + e)

