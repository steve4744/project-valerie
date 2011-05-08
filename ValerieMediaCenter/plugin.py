# -*- coding: utf-8 -*-

from Components.config import config
from Plugins.Plugin import PluginDescriptor

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin

#------------------------------------------------------------------------------------------

gE2Control = None
gSessionPV = None
gReasonPV = -1

def autostart(reason, **kwargs):
	global gE2Control
	global gSessionPV
	
	if kwargs.has_key("session"):
		gSessionPV = kwargs["session"]
	printl("Reason: " + str(reason), __name__, "I")
	gReasonPV = reason
	
	from DMC_Global import E2Control
	if gReasonPV == 0 and gSessionPV != None and gE2Control == None:
		gE2Control = E2Control()
	elif gReasonPV == 1 and gE2Control != None:
#		gE2Control.stop()
		gE2Control = None
	
	plugins = getPlugins(where=Plugin.AUTOSTART_E2)
	for plugin in plugins:
		plugin.fnc(gSessionPV)

def PVMC_Wizard(*args, **kwargs):
	import DMC_Wizard
	return DMC_Wizard.PVMC_Wizard(*args, **kwargs)

def PVMC_MainMenu(*args, **kwargs):
	import DMC_MainMenu
	return DMC_MainMenu.PVMC_MainMenu(False, *args, **kwargs)

def PVMC_MainMenuAutostart(*args, **kwargs):
	import DMC_MainMenu
	return DMC_MainMenu.PVMC_MainMenu(True, *args, **kwargs)

def main(session, **kwargs):
	session.open(PVMC_MainMenu)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("Project Valerie"), main, "pvmc_mainmenu", 44)]
	return []

def Plugins(**kwargs):
	list = []
	list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_MENU, fnc = menu))
	list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main))
	if config.plugins.pvmc.showwizard.value == True:
		list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_WIZARD, fnc=(58, PVMC_Wizard)))
	if config.plugins.pvmc.autostart.value == True:
		list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_WIZARD, fnc=(63, PVMC_MainMenuAutostart)))
	
	list.append(PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart))
	
	return list
