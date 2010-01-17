from Plugins.Plugin import PluginDescriptor
from Components.config import config
from DMC_Global import printl
		
#------------------------------------------------------------------------------------------

def main(session, **kwargs):
		session.open(DMC_MainMenu)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("Project Valerie"), main, "dmc_mainmenu", 44)]
	return []

gE2Control = None
gSession = None
gReason = -1

def autostart(reason, **kwargs):
	global gE2Control
	global gSession

	if kwargs.has_key("session"):
                gSession = kwargs["session"]
	printl("Reason: " + str(reason))
	gReason = reason

	from DMC_Global import E2Control
	if gReason == 0 and gSession != None and gE2Control == None:
		gE2Control = E2Control()
	elif gReason == 1 and gE2Control != None:
#		gE2Control.stop()
		gE2Control = None
	

def DMC_Wizard(*args, **kwargs):
	from DMC_Wizard import DMC_Wizard
	return DMC_Wizard(*args, **kwargs)

def DMC_MainMenu(*args, **kwargs):
	from DMC_MainMenu import DMC_MainMenu
	return DMC_MainMenu(*args, **kwargs)

def Plugins(**kwargs):
	list = []
	list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_MENU, fnc = menu))
	if config.plugins.dmc.showwizard.value == True:
		list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_WIZARD, fnc=(58, DMC_Wizard)))
	if config.plugins.dmc.autostart.value == True:
		list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_WIZARD, fnc=(59, DMC_MainMenu)))

	list.append(PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart))

 	return list

