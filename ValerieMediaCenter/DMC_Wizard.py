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
		printl("set config.plugins.dmc.autostart to" + str(selection))
		if selection == "yes":
			config.plugins.dmc.autostart.value = True
		else:
			config.plugins.dmc.autostart.value = False
		printl("config.plugins.dmc.autostart -> " + str(config.plugins.dmc.autostart.value))

	def saveConfig(self):
		config.plugins.dmc.showwizard.value = False
		config.save() 
		printl("Saved !")
