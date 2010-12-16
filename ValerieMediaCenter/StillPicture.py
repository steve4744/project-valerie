from Components.Renderer.Renderer import Renderer

from enigma import eCanvas, eRect
from DMC_Global import Showiframe


class StillPicture(Renderer):
	GUI_WIDGET = eCanvas
	
	element = False
	
	stillpicture = ""
	stillpictureDefault = ""
	
	def __init__(self):
		Renderer.__init__(self)
		self.showiframe = Showiframe()

	def elementExists(self):
		return self.element

	def getStillpicture(self):
		return self.stillpicture

	def getStillpictureDefault(self):
		return self.stillpictureDefault

	def setStillPicture(self, value, default=False, refresh=True):
		if default is True:
			self.stillpictureDefault = value
		
		if self.stillpicture != value:
			self.stillpicture = value
			if refresh is True:
				self.changed()

	def setStillPictureToDefault(self):
		if self.stillpicture != self.stillpictureDefault:
			self.stillpicture = self.stillpictureDefault
			self.changed()

	def postWidgetCreate(self, instance):
		print "postWidgetCreate", instance
		self.sequence = None
		
		if self.skinAttributes is not None:
			self.element = True
			for (attrib, value) in self.skinAttributes:
				if attrib == "id":
					self.setStillPicture(value, True, False)

	def showStillPicture(self):
		if self.elementExists():
			try:
				self.showiframe.showStillpicture(self.getStillpicture())
			except Exception, ex:
				print ex

	def finishStillPicture(self):
		if self.elementExists():
			try:
				self.showiframe.finishStillPicture()
			except Exception, ex:
				print ex

	def onShow(self):
		print "ONSHOW"
		self.showStillPicture()

	def onHide(self):
		print "ONHIDE"
		# We could close the still picutre here, but keep it open for a neatless expereience

	def changed(self):
		print "CHANGED"
		self.showStillPicture()
