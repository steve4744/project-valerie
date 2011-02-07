from Components.Renderer.Renderer import Renderer

from enigma import eWidget, eCanvas, eRect

class eDataElement(eWidget):
	def __init__(self, parent):
		print "eDataElement::__init__", parent
		eWidget.__init__(self, parent)
		self.setTransparent(True)
	
	def setText(self,t):
		print "eDataElement::setText", t

class DataElement(Renderer):
	GUI_WIDGET = eDataElement
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
			if attrib == "text":
				self.setData(value)
