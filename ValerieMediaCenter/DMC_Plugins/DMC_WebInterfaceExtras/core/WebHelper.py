from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Components.config import config
from Components.config import ConfigSelection

import os
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Utf8 = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

##
#
##	
class WebHelper():
	##
	#
	##
	def readFileContent(self, target):
		global Utf8
		global utf8ToLatin
		if Utf8 is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import Utf8
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin	

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

	##
	#
	##
	def prepareTable(self, value, entry, name="value"):
		#print type(value), value
		
		tag = "input"
		configType = "text"
		
		if type(value) is bool:
			configType = "checkbox"
			if value is True:
				configValue = "checked=\"checked\""
			else:
				configValue = ""
		elif type(value) is list or type(value) is tuple:
			choices = value[1]
			configType = "select"
			tag = "select"
			configValue = value[0]
		elif type(entry) is ConfigSelection:
			choices = entry.choices
			configType = "select"
			tag = "select"
			configValue = value
		else:
			configValue = "value=\"%s\"" % value
		
		if tag == "input":
			tag = """<input id="value" name="%s" type="%s" size="50" %s></input>""" % (name, configType, configValue)
		elif tag == "select":
			tag = u"""<select id="value" name="%s">""" % name
			for choice in choices:
				if choice == configValue:
					tag += u"""<option value="%s" size="50" selected>%s</option>""" % (choice, choice)
				else:
					tag += u"""<option value="%s" size="50">%s</option>""" % (choice, choice)
			
			tag += u"""</select>"""
		return (configType, tag, )
		