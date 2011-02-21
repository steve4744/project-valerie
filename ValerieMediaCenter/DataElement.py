from Components.Renderer.Renderer import Renderer
from Components.config import *
from enigma import eWidget, eCanvas, eRect
import skin

class eDataElement(eWidget):
	def __init__(self, parent):
		#print "eDataElement::__init__", parent
		eWidget.__init__(self, parent)
		self.setTransparent(True)
	
	def setText(self,t):
		#print "eDataElement::setText", t
		pass

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
		#print "postWidgetCreate", instance
		self.sequence = None
		
		for (attrib, value) in self.skinAttributes:
			if attrib == "text":
				self.setData(value)


	def getDataPreloading(self, screen, name):
		try:
			for entry in skin.dom_skins:
				if entry[0].startswith(config.plugins.pvmc.skinfolderpath.value):
					for element in entry[1]:
						if 'name' in element.keys() and element.get('name') == screen.skinName:
							for child in element:
								if 'name' in child.keys() and child.get('name') == name:
									return child.get('text')
		except:
			return ""
		return ""