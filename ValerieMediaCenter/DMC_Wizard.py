from Screens.Wizard import WizardSummary
from Screens.WizardLanguage import WizardLanguage
from Components.config import config
from Components.Pixmap import Pixmap
from Components.Label import Label
from DMC_Global import printl

class PVMC_Wizard(WizardLanguage):

	def __init__(self, session):
		self.xmlfile = config.plugins.pvmc.pluginfolderpath.value + "DMC_Wizard.xml"

		WizardLanguage.__init__(self, session, showSteps = False, showStepSlider = False)
		self["wizard"] = Pixmap()
		self["textTop"] = Label()
		self["textCenter"] = Label()
		self["textBottom"] = Label()

	def autostart(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.pvmc.autostart.value = True
		else:
			config.plugins.pvmc.autostart.value = False
		printl("config.plugins.pvmc.autostart -> " + str(config.plugins.pvmc.autostart.value))

	def checkforupdate(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.pvmc.checkforupdate.value = True
		else:
			config.plugins.pvmc.checkforupdate.value = False
		printl("config.plugins.pvmc.checkforupdate -> " + str(config.plugins.pvmc.checkforupdate.value))

	def uselocal(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.pvmc.uselocal.value = True
		else:
			config.plugins.pvmc.uselocal.value = False
		printl("config.plugins.pvmc.uselocal -> " + str(config.plugins.pvmc.uselocal.value))

	def saveConfig(self):
		config.plugins.pvmc.showwizard.value = False
		config.save() 
		printl("Saved !")
