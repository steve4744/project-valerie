from Components.Renderer.Renderer import Renderer
from Components.config import *
from enigma import eWidget, eCanvas, eRect

import skin

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

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
		printl("value=" + str(value), self)
		self.data = value
		return

	def postWidgetCreate(self, instance):
		#print "postWidgetCreate", instance
		self.sequence = None
		
		if self.skinAttributes is not None:
			for (attrib, value) in self.skinAttributes:
				if attrib == "text":
					self.setData(value)
		else:
			printl("self.skinAttributes is None!!!", self)


	def getDataPreloading(self, screen, name):
		printl("screen=" + str(screen.skinName) + " name=" + str(name), self)
		try:
			for entry in skin.dom_skins:
				#print entry[0], " - ", config.plugins.pvmc.skinfolderpath.value
				if entry[0].startswith(config.plugins.pvmc.skinfolderpath.value):
					for element in entry[1]:
						#print element
						if 'name' in element.keys() and element.get('name') == screen.skinName:
							#print element.get('name')
							for child in element:
								if 'name' in child.keys() and child.get('name') == name:
									return child.get('text')
		except Exception, ex:
			printl(str(ex), self)
			return ""
		return ""