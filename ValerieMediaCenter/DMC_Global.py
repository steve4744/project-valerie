from _ctypes import *

class Showiframe():
	def __init__(self):
		self.showiframe = dlopen("libshowiframe.so.0.0.0")
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
