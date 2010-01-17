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

printl("Init")

# the currentVersion should be renewed every major update
currentVersion          = 100
defaultPluginFolderPath = resolveFilename(SCOPE_PLUGINS, "Extensions/MediaCenter/")
defaultSkinFolderPath   = defaultPluginFolderPath + "skins/"
defaultSkin             = "defaultHD/skin.xml"
defaultURL              = "http://project-valerie.googlecode.com/svn/trunk/"
defaultUpdateXML        = "update.xml"

printl("defaultPluginFolderPath=" + defaultPluginFolderPath)
printl("defaultSkinFolderPath=" + defaultSkinFolderPath)

config.plugins.dmc = ConfigSubsection()

config.plugins.dmc.language          = ConfigSelection(default="EN", choices = [("EN", _("English"))])
config.plugins.dmc.showwizard        = ConfigYesNo(default = True)
config.plugins.dmc.autostart         = ConfigYesNo(default = True)
config.plugins.dmc.checkforupdate    = ConfigYesNo(default = True)

printl("language="       + str(config.plugins.dmc.language.value))
printl("showwizard="     + str(config.plugins.dmc.showwizard.value))
printl("autostart="      + str(config.plugins.dmc.autostart.value))
printl("checkforupdate=" + str(config.plugins.dmc.checkforupdate.value))

config.plugins.dmc.version           = ConfigInteger(0, (0, 999))
config.plugins.dmc.pluginfolderpath  = ConfigText(default = defaultPluginFolderPath)
config.plugins.dmc.skinfolderpath    = ConfigText(default = defaultSkinFolderPath)
config.plugins.dmc.skin              = ConfigText(default = defaultSkinFolderPath)
config.plugins.dmc.url               = ConfigText(default = defaultURL)
config.plugins.dmc.updatexml         = ConfigText(default = defaultUpdateXML)

# We updated to a newer version, so redisplay wizard
if config.plugins.dmc.version.value != currentVersion:
	config.plugins.dmc.showwizard.value = True

config.plugins.dmc.version.value     = currentVersion

# Load Skin, first try to find it, if not found reset to default skin
try:
	loadSkin(config.plugins.dmc.skinfolderpath.value + config.plugins.dmc.skin.value)
except Exception, e:
	config.plugins.dmc.skinfolderpath.value = defaultSkinFolderPath
	config.plugins.dmc.skin.value           = defaultSkin
	
	# we could do an try at this point, but if the skin is missing we have lost anyway
	loadSkin(config.plugins.dmc.skinfolderpath.value + config.plugins.dmc.skin.value)

config.save()

