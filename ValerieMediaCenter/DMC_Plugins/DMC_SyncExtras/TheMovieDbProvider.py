# -*- coding: utf-8 -*-
'''
Project Valerie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

DreamPlex Plugin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
'''
#===============================================================================
# IMPORT
#===============================================================================
import re
import json

import Genres
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#===============================================================================
# 
#===============================================================================
class TheMovieDbProvider(object):

	APIKEY = u"351217450d7c7865ca39c74a7e3a0a4b"
	PLOT_MIN_LEN = 10
	
	#################
	# SAMPLE
	#http://api.themoviedb.org/3/movie/tt1411250?api_key=351217450d7c7865ca39c74a7e3a0a4b
	#################
	apiImdbLookup = u"http://api.themoviedb.org/3/movie/<imdbid>?api_key=" + APIKEY + u"&language=<lang>"

	#===============================================================================
	# 
	#===============================================================================
	def getMovieByImdbID(self, info):
		printl ("", self, "S")
		
		if info.ImdbId == info.ImdbIdNull:
			printl("None (info.ImdbId == info.ImdbIdNull)", self, "I") 
			
			printl ("", self, "C")
			return None
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   u"en",	   url)
		result = WebGrabber.getJson(url)
		
		if result is None:
			printl("None (result is None)", self, "I") 
			
			printl ("", self, "C")
			return None
		
		eMovie = json.loads(result)
		tmp = self.getTmdbId(info, eMovie)
		if tmp is not None:
			info = tmp
		#tmp = self.getImdbId(info, eMovie)
		#if tmp is not None:
		#	info = tmp
		tmp = self.getName(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getOverview(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getReleased(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getRating(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getRuntime(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getGenre(info, eMovie)
		if tmp is not None:
			info = tmp

		printl ("", self, "C")		
		return info

	#===============================================================================
	# 
	#===============================================================================
	def getMovie(self, info, lang):
		printl ("", self, "S")
		
		if info.TmDbId == info.TmDbIdNull:
			printl("None (info.TmDbId == info.TmDbIdNull)", self, "I") 
			
			printl ("", self, "C")
			return None
		
		lang = lang.lower()
		
		if lang == u"en":
			printl("en already parsed using getSerieByImdbID()", self, "I")
			
			printl ("", self, "C")
			return info
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   lang,		url)
		result = WebGrabber.getJson(url)
		
		if result is None:
			printl("None (result is None)", self, "I") 
			
			printl ("", self, "C")
			return None
		
		eMovie = json.loads(result)
		
		#if self.getTranslated(eMovie) is False:
		#	continue
		
		#tmp = self.getTmdbId(info, eMovie)
		#if tmp is not None:
		#	info = tmp
		#tmp = self.getImdbId(info, eMovie)
		#if tmp is not None:
		#	info = tmp
		tmp = self.getName(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getOverview(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getReleased(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getRating(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getRuntime(info, eMovie)
		if tmp is not None:
			info = tmp
		tmp = self.getGenre(info, eMovie)
		if tmp is not None:
			info = tmp
		
		printl ("", self, "C")		
		return info

	#===============================================================================
	# 
	#===============================================================================
	def getArtByImdbId(self, info):
		printl ("", self, "S")
		
		if info.ImdbId == info.ImdbIdNull:
			printl("None (info.ImdbId == info.ImdbIdNull)", self, "D")
			
			printl ("", self, "C")
			return None
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   u"en",	   url)
		result = WebGrabber.getJson(url)
		
		if result is None:
			printl("None (result is None)", self, "D") 
			
			printl ("", self, "C")
			return None
		
		eMovie = json.loads(result)
		try:
			info.Poster = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/w300" + eMovie['poster_path']
		except Exception, ex:
			printl("Exception: " + str(ex), self)
			info.Poster = ""
		try:
			info.Backdrop = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/w1000" + eMovie['backdrop_path']
		except Exception, ex:
			printl("Exception: " + str(ex), self)
			info.Backdrop = ""
		
		if len(info.Poster) > 0 or len(info.Backdrop) > 0:
			printl ("we have picture data", self, "D")
			printl ("", self, "C")
			return info
		
		printl ("we have NO picture data", self, "D")
		printl ("", self, "C")
		return None

#===============================================================================
# HELPER
#===============================================================================
	#===============================================================================
	# 
	#===============================================================================
	def getTmdbId(self, info, elem):
		printl ("", self, "S")
		
		try:
			eID = None
			eID = elem['id']
			if eID is not None and eID > 0:
				info.TmDbId = eID
				
				printl ("", self, "C")
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self, "W")
		
		printl ("", self, "C")
		return None

	#===============================================================================
	# 
	#===============================================================================
	def getName(self, info, elem):
		printl ("", self, "S")
		
		try:
			eTitle = None
			eTitle = elem['title']
			if eTitle is not None and len(eTitle) > 0:
				info.Title = eTitle
				
				printl ("", self, "C")
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		printl ("", self, "C")
		return None

	#===============================================================================
	# 
	#===============================================================================
	def getOverview(self, info, elem):
		printl ("", self, "S")
		
		try:
			ePlot = None
			ePlot = elem['overview']
			if ePlot is not None and len(ePlot) > self.PLOT_MIN_LEN:
				info.Plot = re.sub(u"\r\n", u" ", ePlot)
				info.Plot = re.sub(u"\n", u" ", info.Plot)
				info.Plot += u" [TMDB.ORG]" 
				
				printl ("", self, "C")
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		printl ("", self, "C")
		return None

	#===============================================================================
	# 
	#===============================================================================
	def getReleased(self, info, elem):
		printl ("", self, "S")
		
		try:
			eYear = None
			eYear = elem['release_date']
			if eYear is not None and len(eYear) > 0:
				strImdb = eYear
				date = strImdb.split(u"-")
				info.Year = int(date[0])
				info.Month = int(date[1])
				info.Day = int(date[2])
				
				printl ("", self, "C")
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		printl ("", self, "C")
		return None

	#===============================================================================
	# 
	#===============================================================================
	def getRuntime(self, info, elem):
		printl ("", self, "S")
		
		try:
			eRuntime = None
			eRuntime = str(elem['runtime'])
			if eRuntime is not None and len(eRuntime) > 0:
				info.Runtime = int(eRuntime)
				
				printl ("", self, "C")
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		printl ("", self, "C")
		return None

	#===============================================================================
	# 
	#===============================================================================
	def getRating(self, info, elem):
		printl ("", self, "S")
		
		try:
			eRating = None
			eRating = str(elem['vote_average'])
			if eRating is not None and len(eRating) > 0:
				strRating = eRating
				if strRating != u"0.0":
					pos = strRating.find(u".")
					if pos > 0:
						strRating = strRating[0:pos]
					info.Popularity = int(strRating)
					
					printl ("", self, "C")
					return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		printl ("", self, "C")
		return None  

	#===============================================================================
	# 
	#===============================================================================
	def getGenre(self, info, elem):
		printl ("", self, "S")
		
		genre = u""
		try:
			genreList = elem['genres']
			for genreListItem in genreList:
				genre += genreListItem['name'] + u"|"
			if len(genre) > 0:
				info.Genres = genre[:len(genre) - 1] # Remove the last pipe
				
				printl ("", self, "C")
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		printl ("", self, "C")
		return None
