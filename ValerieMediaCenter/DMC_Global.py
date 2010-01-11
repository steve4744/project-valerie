from _ctypes import *

class Showiframe():
	def __init__(self):
		self.showiframe = dlopen("libshowiframe.so.0.0.0")
		self.showSinglePic = dlsym(showiframe, "_Z13showSinglePicPKc")
		self.finishShowSinglePic = dlsym(showiframe, "_Z19finishShowSinglePicv")

	def  showStillpicture(pic):
		call_function(self.showSinglePic, (pic, ))

	def finishStillPicture():
		call_function(self.finishShowSinglePic, ())
		#dlclose(self.showiframe)

#------------------------------------------------------------------------------------------
