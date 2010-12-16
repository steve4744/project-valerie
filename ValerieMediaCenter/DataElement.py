from Components.Renderer.Renderer import Renderer

from enigma import eCanvas, eRect

class DataElement(Renderer):
	GUI_WIDGET = eCanvas
	data = ""
	def __init__(self):
		Renderer.__init__(self)

	def getData(self):
		return self.data

	def setData(self, value):
		print "setData", value
		self.data = value
		return

	def postWidgetCreate(self, instance):
		print "postWidgetCreate", instance
		self.sequence = None

		for (attrib, value) in self.skinAttributes:
			if attrib == "id":
				self.setData(value)
