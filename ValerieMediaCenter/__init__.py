import Plugins.Plugin
from Components.config import config
from Components.config import ConfigSubsection
from Components.config import ConfigSelection
from Components.config import ConfigInteger
from Components.config import ConfigSubList
from Components.config import ConfigSubDict
from Components.config import ConfigText
from Components.config import configfile
from Components.config import ConfigYesNo
from skin import loadSkin
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from DMC_Global import printl
from enigma import getDesktop

printl("Init")

# the currentVersion should be renewed every major update
currentVersion          = "r001"
defaultPluginFolderPath = resolveFilename(SCOPE_PLUGINS, "Extensions/MediaCenter/")
defaultSkinFolderPath   = defaultPluginFolderPath + "skins/"
defaultSkin             = "default"
defaultURL              = "http://www.duckbox.info/valerie/"
defaultUpdateXML        = "update.xml"

printl("defaultPluginFolderPath=" + defaultPluginFolderPath)
printl("defaultSkinFolderPath=" + defaultSkinFolderPath)

config.plugins.dmc = ConfigSubsection()

config.plugins.dmc.language          = ConfigSelection(default="EN", choices = [("EN", _("English"))])
config.plugins.dmc.showwizard        = ConfigYesNo(default = True)
config.plugins.dmc.autostart         = ConfigYesNo(default = True)
config.plugins.dmc.checkforupdate    = ConfigYesNo(default = True)

config.plugins.dmc.uselocal           = ConfigYesNo(default = False)

printl("language="       + str(config.plugins.dmc.language.value))
printl("showwizard="     + str(config.plugins.dmc.showwizard.value))
printl("autostart="      + str(config.plugins.dmc.autostart.value))
printl("checkforupdate=" + str(config.plugins.dmc.checkforupdate.value))
printl("uselocal=" + str(config.plugins.dmc.uselocal.value))

config.plugins.dmc.version           = ConfigText(default = "r001")
config.plugins.dmc.pluginfolderpath  = ConfigText(default = defaultPluginFolderPath)
config.plugins.dmc.skinfolderpath    = ConfigText(default = defaultSkinFolderPath)
config.plugins.dmc.skin              = ConfigText(default = defaultSkin)
config.plugins.dmc.url               = ConfigText(default = defaultURL)
config.plugins.dmc.updatexml         = ConfigText(default = defaultUpdateXML)



# We updated to a newer version, so redisplay wizard
if config.plugins.dmc.version.value != currentVersion:
	config.plugins.dmc.showwizard.value = True

config.plugins.dmc.version.value     = currentVersion

dSize = getDesktop(0).size()


# Load Skin, first try to find it, if not found reset to default skin
skinLoaded = False
try:
	loadSkin(config.plugins.dmc.skinfolderpath.value + config.plugins.dmc.skin.value + "/" + str(dSize.width()) + "x" + str(dSize.height()) + "/skin.xml")
	skinLoaded = True
except Exception, e:
	print e
	skinLoaded = False
	config.plugins.dmc.skinfolderpath.value = defaultSkinFolderPath
	config.plugins.dmc.skin.value           = defaultSkin
	
if skinLoaded == False:
	try:
		loadSkin(config.plugins.dmc.skinfolderpath.value + config.plugins.dmc.skin.value + "/" + str(dSize.width()) + "x" + str(dSize.height()) + "/skin.xml")
		skinLoaded = True
	except Exception, e:
		print e
		skinLoaded = False
		config.plugins.dmc.skinfolderpath.value = defaultSkinFolderPath
		config.plugins.dmc.skin.value           = defaultSkin


config.save()

