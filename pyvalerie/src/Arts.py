# -*- coding: utf-8 -*-

from os import path

import Config
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class Arts():
	
	URL = "http://val.duckbox.info"

	def __init__(self):
		pass

	def download(self, eInfo):
		if eInfo.isMovie:
			if len(eInfo.Poster):
				if path.isfile(WebGrabber.downloadDir + "/" + eInfo.ImdbId + "_poster.png") is False:
					url = WebGrabber.getText(self.URL + "/cgi-bin/convert.py?" + eInfo.ImdbId + ";poster;" + eInfo.Poster)
					if url is not None and url != "NONE":
						WebGrabber.getFile(self.URL + url, eInfo.ImdbId + "_poster.png")
			
			if len(eInfo.Backdrop):
				if path.isfile(WebGrabber.downloadDir + "/" + eInfo.ImdbId + "_backdrop.m1v") is False or path.isfile(WebGrabber.downloadDir + "/" + eInfo.ImdbId + "_backdrop_low.m1v") is False or path.isfile(WebGrabber.downloadDir + "/" + eInfo.ImdbId + "_backdrop.png") is False:
					url = WebGrabber.getText(self.URL + "/cgi-bin/convert.py?" + eInfo.ImdbId + ";backdrop;" + eInfo.Backdrop)
					if url is not None and url != "NONE":
						urls = url.split("<br />")
						if urls is not None and len(urls) >= 3:
							WebGrabber.getFile(self.URL + urls[0].strip(), eInfo.ImdbId + "_backdrop.m1v")
							WebGrabber.getFile(self.URL + urls[1].strip(), eInfo.ImdbId + "_backdrop_low.m1v")
							WebGrabber.getFile(self.URL + urls[2].strip(), eInfo.ImdbId + "_backdrop.png")
		
		elif eInfo.isSerie:
			if len(eInfo.Poster):
				if path.isfile(WebGrabber.downloadDir + "/" + eInfo.TheTvDbId + "_poster.png") is False:
					url = WebGrabber.getText(self.URL + "/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";poster;" + eInfo.Poster)
					if url != "NONE":
						WebGrabber.getFile(self.URL + url, eInfo.TheTvDbId + "_poster.png")
			
			if len(eInfo.Backdrop):
				if path.isfile(WebGrabber.downloadDir + "/" + eInfo.TheTvDbId + "_backdrop.m1v") is False or path.isfile(WebGrabber.downloadDir + "/" + eInfo.TheTvDbId + "_backdrop_low.m1v") is False or path.isfile(WebGrabber.downloadDir + "/" + eInfo.TheTvDbId + "_backdrop.png") is False:
					url = WebGrabber.getText(self.URL + "/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";backdrop;" + eInfo.Backdrop)
					if url is not None and url != "NONE":
						urls = url.split("<br />")
						if urls is not None and len(urls) >= 3:
							WebGrabber.getFile(self.URL + urls[0].strip(), eInfo.TheTvDbId + "_backdrop.m1v")
							WebGrabber.getFile(self.URL + urls[1].strip(), eInfo.TheTvDbId + "_backdrop_low.m1v")
							WebGrabber.getFile(self.URL + urls[2].strip(), eInfo.TheTvDbId + "_backdrop.png")
