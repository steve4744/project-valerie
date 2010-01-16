from Plugins.Plugin import PluginDescriptor
from Components.config import config
		
#------------------------------------------------------------------------------------------

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("Project Valerie"), DMC_MainMenu, "dmc_mainmenu", 44)]
	return []

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
 	return list

