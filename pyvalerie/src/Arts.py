# -*- coding: utf-8 -*-

from os import path

import Config
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class Arts():
	
	URL = "http://val.duckbox.info"
	CONVERT = "/cgi-bin/convert2.py?"

	posterResolution = ("110x214", "156x214", "195x267", )

	def __init__(self):
		pass

	def isMissing(self, eInfo):
		if eInfo.isTypeMovie():
			if path.isfile(WebGrabber.downloadDir + "/" + eInfo.ImdbId + "_poster_" + self.posterResolution[0] + ".png") is False:
				return True
			if path.isfile(WebGrabber.downloadDir + "/" + eInfo.ImdbId + "_backdrop.m1v") is False:
				return True
		
		elif eInfo.isTypeSerie() or eInfo.isTypeEpisode():
			if path.isfile(WebGrabber.downloadDir + "/" + eInfo.TheTvDbId + "_poster_" + self.posterResolution[0] + ".png") is False:
				return True
			if path.isfile(WebGrabber.downloadDir + "/" + eInfo.TheTvDbId + "_backdrop.m1v") is False:
				return True
		return False

	def save(self, url):
		urlresponse = WebGrabber.getText(url)
		printl("urlresponse=" + str(urlresponse), self, "D")
		if urlresponse is not None and urlresponse != "NONE":
			urlresponse = urlresponse.strip().split("<br />")
			for file in urlresponse:
				fileInfo = file.strip().split('|')
				printl("fileInfo=" + str(fileInfo), self, "D")
				if len(fileInfo) == 2:
					WebGrabber.getFile(self.URL + fileInfo[1], fileInfo[0])

	def download(self, eInfo):
		printl("->", self, "D")
		if eInfo.isTypeMovie():
			if len(eInfo.Poster):
				isMissing = False
				if path.isfile(WebGrabber.downloadDir + "/" + eInfo.ImdbId + "_poster_" + self.posterResolution[0] + ".png") is False:
					self.save(self.URL + self.CONVERT + eInfo.ImdbId + ";poster;" + eInfo.Poster)
			
			if len(eInfo.Backdrop):
				if path.isfile(WebGrabber.downloadDir + "/" + eInfo.ImdbId + "_backdrop.m1v") is False:
					self.save(self.URL + self.CONVERT + eInfo.ImdbId + ";backdrop;" + eInfo.Backdrop)
		
		elif eInfo.isTypeSerie() or eInfo.isTypeEpisode():
			if len(eInfo.Poster):
				if path.isfile(WebGrabber.downloadDir + "/" + eInfo.TheTvDbId + "_poster_" + self.posterResolution[0] + ".png") is False:
					self.save(self.URL + self.CONVERT + eInfo.TheTvDbId + ";poster;" + eInfo.Poster)
			
			if len(eInfo.Backdrop):
				if path.isfile(WebGrabber.downloadDir + "/" + eInfo.TheTvDbId + "_backdrop.m1v") is False:
					self.save(self.URL + self.CONVERT + eInfo.TheTvDbId + ";backdrop;" + eInfo.Backdrop)
		printl("<-", self, "D")
