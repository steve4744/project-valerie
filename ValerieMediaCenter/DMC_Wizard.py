from Screens.Wizard import WizardSummary
from Screens.WizardLanguage import WizardLanguage
from Components.config import config
from Components.Pixmap import Pixmap
from Components.Label import Label
from DMC_Global import printl

class DMC_Wizard(WizardLanguage):

	def __init__(self, session):
		self.xmlfile = config.plugins.dmc.pluginfolderpath.value + "DMC_Wizard.xml"

		WizardLanguage.__init__(self, session, showSteps = False, showStepSlider = False)
		self["wizard"] = Pixmap()
		self["textTop"] = Label()
		self["textCenter"] = Label()
		self["textBottom"] = Label()

	def autostart(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.dmc.autostart.value = True
		else:
			config.plugins.dmc.autostart.value = False
		printl("config.plugins.dmc.autostart -> " + str(config.plugins.dmc.autostart.value))

	def checkforupdate(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.dmc.checkforupdate.value = True
		else:
			config.plugins.dmc.checkforupdate.value = False
		printl("config.plugins.dmc.checkforupdate -> " + str(config.plugins.dmc.checkforupdate.value))

	def uselocal(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.dmc.uselocal.value = True
		else:
			config.plugins.dmc.uselocal.value = False
		printl("config.plugins.dmc.uselocal -> " + str(config.plugins.dmc.uselocal.value))

	def saveConfig(self):
		config.plugins.dmc.showwizard.value = False
		config.save() 
		printl("Saved !")
