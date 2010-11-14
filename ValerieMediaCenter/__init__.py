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
defaultPluginFolderPath = resolveFilename(SCOPE_PLUGINS, "Extensions/ProjectValerie/")
defaultSkinFolderPath   = defaultPluginFolderPath + "skins/"
defaultSkin             = "default"
defaultURL              = "http://www.duckbox.info/valerie/"
defaultUpdateXML        = "update.php"

printl("defaultPluginFolderPath=" + defaultPluginFolderPath)
printl("defaultSkinFolderPath=" + defaultSkinFolderPath)

config.plugins.pvmc = ConfigSubsection()

config.plugins.pvmc.language          = ConfigSelection(default="EN", choices = [("EN", _("English"))])
config.plugins.pvmc.showwizard        = ConfigYesNo(default = True)
config.plugins.pvmc.autostart         = ConfigYesNo(default = True)
config.plugins.pvmc.checkforupdate    = ConfigYesNo(default = True)

config.plugins.pvmc.backdropquality   = ConfigSelection(default="High", choices = ["High", "Low", ])
config.plugins.pvmc.uselocal          = ConfigYesNo(default = False)

printl("language="       + str(config.plugins.pvmc.language.value))
printl("showwizard="     + str(config.plugins.pvmc.showwizard.value))
printl("autostart="      + str(config.plugins.pvmc.autostart.value))
printl("checkforupdate=" + str(config.plugins.pvmc.checkforupdate.value))
printl("uselocal=" + str(config.plugins.pvmc.uselocal.value))

config.plugins.pvmc.version           = ConfigText(default = "r001")
config.plugins.pvmc.pluginfolderpath  = ConfigText(default = defaultPluginFolderPath)
config.plugins.pvmc.skinfolderpath    = ConfigText(default = defaultSkinFolderPath)
config.plugins.pvmc.skin              = ConfigText(default = defaultSkin)
config.plugins.pvmc.url               = ConfigText(default = defaultURL)
config.plugins.pvmc.updatexml         = ConfigText(default = defaultUpdateXML)



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
except Exception, e:
	print e
	skinLoaded = False
	config.plugins.pvmc.skinfolderpath.value = defaultSkinFolderPath
	config.plugins.pvmc.skin.value           = defaultSkin
	
if skinLoaded == False:
	try:
		loadSkin(config.plugins.pvmc.skinfolderpath.value + config.plugins.pvmc.skin.value + "/" + str(dSize.width()) + "x" + str(dSize.height()) + "/skin.xml")
		skinLoaded = True
	except Exception, e:
		print e
		skinLoaded = False
		config.plugins.pvmc.skinfolderpath.value = defaultSkinFolderPath
		config.plugins.pvmc.skin.value           = defaultSkin


config.save()

