# -*- coding: utf-8 -*-

import os
import sys

from enigma import getDesktop
from skin import loadSkin
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

#Cannot import printl2 here cause cofnig.pvmc not ready
#from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import loadPlugins

#------------------------------------------------------------------------------------------

print "[valerie] I  __init__:: Init Valerie"

# On Dreamboxes the default encoding should already be uft8
# But on other boxes it may be latin-1 so set it here, and hopefully this will
# not crash anything for those boxes
defaultEncoding = "utf-8"
reload(sys)
sys.setdefaultencoding(defaultEncoding)
print "[valerie] I  __init__:: Default encoding set to: " + defaultEncoding

# the currentVersion should be renewed every major update
currentVersion          = "r001"
defaultPluginFolderPath = resolveFilename(SCOPE_PLUGINS, "Extensions/ProjectValerie/")
defaultSkinFolderPath   = defaultPluginFolderPath + "skins/"
defaultConfigFolderPath = "/hdd/valerie/"
defaultMediaFolderPath  = defaultConfigFolderPath + "media/"
defaultTmpFolderPath    = "/tmp/valerie/"
defaultSkin             = "blackSwan"
defaultURL              = "http://www.duckbox.info/valerie/"
defaultUpdateXML        = "update.php"

config.plugins.pvmc = ConfigSubsection()

config.plugins.pvmc.language          = ConfigSelection(default="EN", choices = [("EN", _("English"))])
config.plugins.pvmc.showwizard        = ConfigYesNo(default = True)
config.plugins.pvmc.autostart         = ConfigYesNo(default = True)
config.plugins.pvmc.checkforupdate    = ConfigYesNo(default = True)

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

config.plugins.pvmc.usepaginationinwebif = ConfigYesNo(default = False)

config.plugins.pvmc.save()

config.plugins.pvwebif = ConfigSubsection()

config.plugins.pvwebif.usepagination = ConfigYesNo(default = True)

config.plugins.pvwebif.save()

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
print "__init__:: version="        + str(config.plugins.pvmc.version.value)
printl("__init__:: version="        + str(config.plugins.pvmc.version.value))
printl("__init__:: language="       + str(config.plugins.pvmc.language.value))
printl("__init__:: showwizard="     + str(config.plugins.pvmc.showwizard.value))
printl("__init__:: autostart="      + str(config.plugins.pvmc.autostart.value))
printl("__init__:: checkforupdate=" + str(config.plugins.pvmc.checkforupdate.value))
printl("__init__:: uselocal=" + str(config.plugins.pvmc.uselocal.value))

skins = []
try:
	for skin in os.listdir(config.plugins.pvmc.skinfolderpath.value):
		if os.path.isdir(os.path.join(config.plugins.pvmc.skinfolderpath.value, skin)) and skin != ".svn":
			skins.append(skin)
except Exception, ex:
	printl("__init__:: Exception(" + str(type(ex)) + "): " + str(ex), None, "W")
	skins.append(defaultSkin)
#config.plugins.pvmc.skin              = ConfigText(default = defaultSkin)
config.plugins.pvmc.skin              = ConfigSelection(default = defaultSkin, choices = skins)
config.plugins.pvmc.url               = ConfigText(default = defaultURL)
config.plugins.pvmc.updatexml         = ConfigText(default = defaultUpdateXML)

config.plugins.pvmc.plugins = ConfigSubsection()

# We updated to a newer version, so redisplay wizard
if config.plugins.pvmc.version.value != currentVersion:
	config.plugins.pvmc.showwizard.value = True

config.plugins.pvmc.version.value     = currentVersion

dSize = getDesktop(0).size()

# Load Skin, first try to find it, if not found reset to default skin
skinLoaded = False
try:
	loadSkin(config.plugins.pvmc.skinfolderpath.value + config.plugins.pvmc.skin.value + "/" + str(dSize.width()) + "x" + str(dSize.height()) + "/skin.xml")
	skinLoaded = True
except Exception, ex:
	printl("__init__:: Exception(" + str(type(ex)) + "): " + str(ex), None, "W")
	skinLoaded = False
	config.plugins.pvmc.skinfolderpath.value = defaultSkinFolderPath
	config.plugins.pvmc.skin.value           = defaultSkin
	
if skinLoaded == False:
	try:
		loadSkin(config.plugins.pvmc.skinfolderpath.value + config.plugins.pvmc.skin.value + "/" + str(dSize.width()) + "x" + str(dSize.height()) + "/skin.xml")
		skinLoaded = True
	except Exception, ex:
		printl("__init__:: Exception(" + str(type(ex)) + "): " + str(ex), None, "W")
		skinLoaded = False
		config.plugins.pvmc.skinfolderpath.value = defaultSkinFolderPath
		config.plugins.pvmc.skin.value           = defaultSkin

loadPlugins(config.plugins.pvmc.pluginfolderpath.value, "Plugins.Extensions.ProjectValerie.")
loadPlugins(config.plugins.pvmc.pluginfolderpath.value + "/DMC_Plugins", "Plugins.Extensions.ProjectValerie.DMC_Plugins.")

config.plugins.pvmc.save()
config.save()
