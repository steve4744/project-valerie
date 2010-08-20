from Plugins.Plugin import PluginDescriptor
from Components.config import config
from DMC_Global import printl
		
#------------------------------------------------------------------------------------------

def main(session, **kwargs):
		session.open(PVMC_MainMenu)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("Project Valerie"), main, "pvmc_mainmenu", 44)]
	return []

gE2Control = None
gSessionPV = None
gReasonPV = -1

def autostart(reason, **kwargs):
	global gE2Control
	global gSessionPV

	if kwargs.has_key("session"):
                gSessionPV = kwargs["session"]
	printl("Reason: " + str(reason))
	gReasonPV = reason

	from DMC_Global import E2Control
	if gReasonPV == 0 and gSessionPV != None and gE2Control == None:
		gE2Control = E2Control()
	elif gReasonPV == 1 and gE2Control != None:
#		gE2Control.stop()
		gE2Control = None
	

def PVMC_Wizard(*args, **kwargs):
	from DMC_Wizard import PVMC_Wizard
	return PVMC_Wizard(*args, **kwargs)

def PVMC_MainMenu(*args, **kwargs):
	from DMC_MainMenu import PVMC_MainMenu
	return PVMC_MainMenu(*args, **kwargs)

def Plugins(**kwargs):
	list = []
	list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_MENU, fnc = menu))
	if config.plugins.pvmc.showwizard.value == True:
		list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_WIZARD, fnc=(58, PVMC_Wizard)))
	if config.plugins.pvmc.autostart.value == True:
		list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_WIZARD, fnc=(59, PVMC_MainMenu)))

	list.append(PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart))

 	return list

