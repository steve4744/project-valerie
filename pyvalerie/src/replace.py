# -*- coding: utf-8 -*-

import os
import re

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

replacementsOptions = ["pre", "post_tv", "post_movie"]
replacementsList = {}

def load():
	# Check default config
	try:
		printl("Check "+"/hdd/valerie/pre.conf", __name__)
		if os.path.isfile("/hdd/valerie/pre.conf") is False:
			f = open("/hdd/valerie/pre.conf", "w")
			f.write('"^\S*-"=" "\n')
			f.write('" (720p|1080i|1080p)( |$)+"=" "\n')
			f.write('" (x264|blu-ray|hdtv|xvid)( |$)+"=" "\n')
			f.write('" (eng|rus)( |$)+"=" "\n')
			f.write('" (oar)( |$)+"=" "\n')
			f.write('" (miniseries)( |$)+"=" "\n')
			f.write('" (dts|dd5|ac3|stereo)( |$)+"=" "\n')
			f.close()
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	try:
		printl("Check "+"/hdd/valerie/post_movie.conf", __name__)
		if os.path.isfile("/hdd/valerie/post_movie.conf") is False:
			f = open("/hdd/valerie/post_movie.conf", "w")
			f.write('" disk\d+( |$)+"=" "\n')
			f.write('" part\d+( |$)+"=" "\n')
			f.write('" extended edition( |$)+"=" "\n')
			f.close()
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	try:
		printl("Check "+"/hdd/valerie/post_tv.conf", __name__)
		if os.path.isfile("/hdd/valerie/post_tv.conf") is False:
			f = open("/hdd/valerie/post_tv.conf", "w")
			f.write('" (oar|esir|miniseries)"=" "\n')
			f.write('"halycon-"=" "\n')
			f.write('"e7-"=" "\n')
			f.close()
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	for rf in replacementsOptions:
		replacementsList[rf] = []
		try:
			f = open("/hdd/valerie/" + rf + ".conf", "r")
			for line in f.readlines():
				keys = line.split("=")
				if len(keys) == 2:
					keys[0] = keys[0].strip().strip('[\'\"]')
					keys[1] = keys[1].strip().strip('[\'\"]')
					printl("[" + str(rf) + "] " + str(keys[0]) + " --> " + str(keys[1]), __name__)
					replacementsList[rf].append([re.compile(keys[0]),keys[1]])
					#replacementsList[rf].append([keys[0],keys[1]])
			f.flush()
			f.close()
		except Exception, ex:
			printl("Exception: " + str(ex), __name__)
			printl("No " + "/hdd/valerie/" + str(rf) + ".conf" + " available", __name__)

def replacements(option):
	if option in replacementsOptions:
		return replacementsList[option]
	else:
		return {}
