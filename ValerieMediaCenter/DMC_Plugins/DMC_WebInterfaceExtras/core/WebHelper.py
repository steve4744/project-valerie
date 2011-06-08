# -*- coding: utf-8 -*-
from threading import Thread

from Components.config import config
from Components.config import ConfigInteger
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

gAvailable = False
try:
	from twisted.web.server import Site
	from twisted.web.static import File
	from twisted.internet   import reactor, threads
	from twisted.web.resource import Resource
	try:
		from Plugins.Extensions.ProjectValerieSync.Manager import Manager
		from Plugins.Extensions.ProjectValerieSync.MediaInfo import *
		from Plugins.Extensions.ProjectValerieSync.Utf8 import *
	except:
		from ..ProjectValerieSync.Manager import Manager
		from ..ProjectValerieSync.MediaInfo import *
		from ..ProjectValerieSync.Utf8 import *
	
	gAvailable = True
except Exception, ex:
	printl("DMC_WebInterfaceExtras::isAvailable Is not available", None, "E")
	printl("DMC_WebInterfaceExtras::isAvailable Exception: " + str(ex), None, "E")
	gAvailable = False

config.plugins.pvmc.plugins.webinterface = ConfigSubsection()
config.plugins.pvmc.plugins.webinterface.port = ConfigInteger(default = 8888, limits=(1, 65535) )
##
#
##	
class WebHelper():
	##
	#
	##
	def readFileContent(self, target):
		c = Utf8(config.plugins.pvmc.pluginfolderpath.value + target, "r")
		content = c.read()
		c.close()
		
		return utf8ToLatin(content)
	##
	#
	##
	def redirectMeTo(self, url):
		redirectHeader =  """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
							<html xmlns="http://www.w3.org/1999/xhtml">
							<head>
							<meta HTTP-EQUIV="REFRESH" content="0; url=%s">
							</head>
							<body>
							</body>
							</html>
						""" % url

		return redirectHeader
		
	##
	#
	##
	def recursive_zip(self, zipf, directory, folder = ""):
		for item in os.listdir(directory):
			if os.path.isfile(os.path.join(directory, item)):
				zipf.write(os.path.join(directory, item), folder + os.sep + item)
			elif os.path.isdir(os.path.join(directory, item)):
				self.recursive_zip(zipf, os.path.join(directory, item), folder + os.sep + item)
