# -*- coding: utf-8 -*-

import re

import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class GoogleProvider():

	URL = u"http://www.google.com/"
	apiSearch = URL + u"search?q=<search>"	
	
	DIV_RESULT_START = u"<li class=g>"
	DIV_RESULT_FLAG = u"<h3 class=\"r\">"

	def searchForSeasonAndEpisode(self, info, result):
		m = re.search(r's(?P<season>\d+)e(?P<episode>\d+)', result)
		if m and m.group("season") and m.group("episode"):
			printl("m.group()=" + str(m.group()), self)
			info.Season = int(m.group("season"))
			info.Episode = int(m.group("episode"))
			return info
		return None

	def getSeasonAndEpisodeFromEpisodeName(self, info):
		if info.SearchString is None or len(info.SearchString) == 0:
			printl(" <- None (info.SearchString is None or len(info.SearchString) == 0)", self) 
			return None
		
		url = self.apiSearch
		url = re.sub("<search>", info.SearchString, url)
		html = WebGrabber.getHtml(url)
		
		if html is None:
			printl(" <- None (html is None)", self) 
			return None
		
		# well there seems to be a problem with detecting tvshows,
		#so lets build in a workaround, you will need at least 2 time the same
		#season and episode before acepting it
		
		count = 0
		s = 0
		e = 0
		
		htmlSplitted = html.split(self.DIV_RESULT_START)
		for htmlSplitter in htmlSplitted:
			htmlSplitter = htmlSplitter.strip()
			if htmlSplitter.startswith(self.DIV_RESULT_FLAG) is False:
				continue
			
			#pos = htmlSplitter.find(self.DIV_RESULT_END)
			#if pos < 0:
			#	continue
			
			tmp = self.searchForSeasonAndEpisode(info, htmlSplitter.lower())
			if tmp is not None:
				info = tmp
				
				if s == 0 or e == 0:
					s = info.Season
					e = info.Episode
				
				if s == info.Season and e == info.Episode:
					count = count + 1
					if count == 2:
						return info
			else:
				continue
		
		printl(" <- None (eof)", self) 
		return None
