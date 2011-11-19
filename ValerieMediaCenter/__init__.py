# -*- coding: utf-8 -*-

import os
import sys

from enigma import getDesktop
from skin import loadSkin, loadSingleSkinData
from Components.config import config
from Components.config import ConfigSubsection
from Components.config import ConfigSelection
from Components.config import ConfigInteger
from Components.config import ConfigSubList
from Components.config import ConfigSubDict
from Components.config import ConfigText
from Components.config import configfile
from Components.config import ConfigYesNo
from Components.config import ConfigPassword
import Plugins.Plugin
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

#Cannot import log here cause config.pvmc not ready
from Plugins.Extensions.ProjectValerie.__plugin__ import loadPlugins
from Plugins.Extensions.ProjectValerie.DMC_Global import findSkin

#------------------------------------------------------------------------------------------

print "[PVMC STARTING] I  __init__:: Init Valerie"

# the currentVersion should be renewed every major update
currentVersion          = "r001"
defaultPluginFolderPath = resolveFilename(SCOPE_PLUGINS, "Extensions/ProjectValerie/")
defaultSkinFolderPath   = defaultPluginFolderPath + "skins/"
defaultConfigFolderPath = "/hdd/valerie/"
defaultMediaFolderPath  = defaultConfigFolderPath + "media/"
defaultTmpFolderPath    = "/tmp/valerie/"
defaultSkin             = "blackSwan"
defaultURL              = "http://val.duckbox.info/"
defaultUpdateXML        = "update.php"

config.plugins.pvmc = ConfigSubsection()

config.plugins.pvmc.language          = ConfigSelection(default="EN", choices = [("EN", _("English"))])
config.plugins.pvmc.showwizard        = ConfigYesNo(default = True)
config.plugins.pvmc.autostart         = ConfigYesNo(default = True)
config.plugins.pvmc.checkforupdate    = ConfigSelection(default = "Passive", choices = ["Active", "Passive", "Off", ])
config.plugins.pvmc.updatetype        = ConfigSelection(default = "Release", choices = ["Release", "Nightly", ])
config.plugins.pvmc.debugMode         = ConfigSelection(default="Silent", choices = ["High", "Normal", "Silent", ])

config.plugins.pvmc.showmovieandtvinmainmenu    = ConfigYesNo(default = False)
config.plugins.pvmc.onpowerpress      = ConfigSelection(default="DeepStandby", choices = ["DeepStandby", "Standby", ])
config.plugins.pvmc.backdropquality   = ConfigSelection(default="High", choices = ["High", "Low", ])
config.plugins.pvmc.uselocal          = ConfigYesNo(default = False)

config.plugins.pvmc.version           = ConfigText(default = "r001")
config.plugins.pvmc.pluginfolderpath  = ConfigText(default = defaultPluginFolderPath)
config.plugins.pvmc.skinfolderpath    = ConfigText(default = defaultSkinFolderPath)

config.plugins.pvmc.configfolderpath    = ConfigText(default = defaultConfigFolderPath)
config.plugins.pvmc.mediafolderpath     = ConfigText(default = defaultMediaFolderPath)
config.plugins.pvmc.tmpfolderpath       = ConfigText(default = defaultTmpFolderPath)
config.plugins.pvmc.showseenforshow     = ConfigYesNo(default = False)
config.plugins.pvmc.showseenforseason   = ConfigYesNo(default = False)

config.plugins.pvmc.save()

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
printl("__init__:: version="        + str(config.plugins.pvmc.version.value))
printl("__init__:: language="       + str(config.plugins.pvmc.language.value))
printl("__init__:: showwizard="     + str(config.plugins.pvmc.showwizard.value))
printl("__init__:: autostart="      + str(config.plugins.pvmc.autostart.value))
printl("__init__:: checkforupdate=" + str(config.plugins.pvmc.checkforupdate.value))
printl("__init__:: updatetype="     + str(config.plugins.pvmc.updatetype.value))
printl("__init__:: uselocal=" 		+ str(config.plugins.pvmc.uselocal.value))
printl("__init__:: debugMode=" 		+ str(config.plugins.pvmc.debugMode.value))

skins = []
try:
	for skin in os.listdir(config.plugins.pvmc.skinfolderpath.value):
		if os.path.isdir(os.path.join(config.plugins.pvmc.skinfolderpath.value, skin)) and skin != ".svn":
			skins.append(skin)
except Exception, ex:
	printl("__init__:: Exception(" + str(type(ex)) + "): " + str(ex), None, "W")
	skins.append(defaultSkin)

config.plugins.pvmc.skin              = ConfigSelection(default = defaultSkin, choices = skins)
config.plugins.pvmc.url               = ConfigText(default = defaultURL)
config.plugins.pvmc.updatexml         = ConfigText(default = defaultUpdateXML)

config.plugins.pvmc.plugins = ConfigSubsection()

# TODO COULD BE DELETED IN MY POINT OF VIEW
# We updated to a newer version, so redisplay wizard
if config.plugins.pvmc.version.value != currentVersion:
	config.plugins.pvmc.showwizard.value = True

config.plugins.pvmc.version.value     = currentVersion

dSize = getDesktop(0).size()

# Load Skin, first try to find it, if not found reset to default skin
skinLoaded = False
try:
	skinPath = config.plugins.pvmc.skinfolderpath.value + config.plugins.pvmc.skin.value + "/" + str(dSize.width()) + "x" + str(dSize.height()) + "/"
	loadSkin(skinPath + "skin.xml")
	loadSingleSkinData(getDesktop(0), findSkin(), skinPath)
	skinLoaded = True
except Exception, ex:
	printl("__init__:: Exception(" + str(type(ex)) + "): " + str(ex), None, "W")
	skinLoaded = False
	config.plugins.pvmc.skinfolderpath.value = defaultSkinFolderPath
	config.plugins.pvmc.skin.value           = defaultSkin
	
if skinLoaded == False:
	try:
		skinPath = config.plugins.pvmc.skinfolderpath.value + config.plugins.pvmc.skin.value + "/" + str(dSize.width()) + "x" + str(dSize.height()) + "/"
		loadSkin(skinPath + "skin.xml")
		loadSingleSkinData(getDesktop(0), findSkin(), skinPath)
		skinLoaded = True
	except Exception, ex:
		printl("__init__:: Exception(" + str(type(ex)) + "): " + str(ex), None, "W")
		skinLoaded = False
		config.plugins.pvmc.skinfolderpath.value = defaultSkinFolderPath
		config.plugins.pvmc.skin.value           = defaultSkin

#We also have to search for Plugins in the main folder as there are main components located (settings general and expert)
loadPlugins(config.plugins.pvmc.pluginfolderpath.value, "Plugins.Extensions.ProjectValerie.")
loadPlugins(config.plugins.pvmc.pluginfolderpath.value + "/DMC_Plugins", "Plugins.Extensions.ProjectValerie.DMC_Plugins.")

config.plugins.pvmc.save()
# Will crash with enigma2 3.2.1 !!!!!!!!!!!!
#config.save()
