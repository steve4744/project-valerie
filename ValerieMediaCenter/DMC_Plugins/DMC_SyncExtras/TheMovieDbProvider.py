# -*- coding: utf-8 -*-

import re
import json

import Genres
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class TheMovieDbProvider(object):

	APIKEY = u"351217450d7c7865ca39c74a7e3a0a4b"
	PLOT_MIN_LEN = 10
	
	#http://api.themoviedb.org/3/movie/tt1411250?api_key=351217450d7c7865ca39c74a7e3a0a4b
	
	#apiImdbLookup = u"http://api.themoviedb.org/2.1/Movie.imdbLookup/<lang>/xml/" + APIKEY + u"/<imdbid>"
	apiImdbLookup = u"http://api.themoviedb.org/3/movie/<imdbid>?api_key=" + APIKEY + u"&language=<lang>"
	apiGetInfo = u"http://api.themoviedb.org/2.1/Movie.getInfo/<lang>/xml/" + APIKEY + u"/<tmdbid>"
	PLOT_MIN_LEN = 10

	def getElem(self, elem, name):
		if elem.getElementsByTagName(name) != None:
			if len(elem.getElementsByTagName(name)) > 0:
				if elem.getElementsByTagName(name)[0] != None:
					if elem.getElementsByTagName(name)[0].childNodes != None:
						if len(elem.getElementsByTagName(name)[0].childNodes) > 0:
							return elem.getElementsByTagName(name)[0].childNodes[0]
		return None

	def getTmdbId(self, info, elem):
		try:
			eID = None
			eID = elem['id']
			if eID is not None and eID > 0:
				info.TmDbId = eID
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getName(self, info, elem):
		try:
			eTitle = None
			eTitle = elem['title']
			if eTitle is not None and len(eTitle) > 0:
				info.Title = eTitle
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getOverview(self, info, elem):
		try:
			ePlot = None
			ePlot = elem['overview']
			if ePlot is not None and len(ePlot) > self.PLOT_MIN_LEN:
				info.Plot = re.sub(u"\r\n", u" ", ePlot)
				info.Plot = re.sub(u"\n", u" ", info.Plot)
				info.Plot += u" [TMDB.ORG]" 
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getReleased(self, info, elem):
		try:
			eYear = None
			eYear = elem['release_date']
			if eYear is not None and len(eYear) > 0:
				strImdb = eYear
				date = strImdb.split(u"-")
				info.Year = int(date[0])
				info.Month = int(date[1])
				info.Day = int(date[2])
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getRuntime(self, info, elem):
		try:
			eRuntime = None
			eRuntime = elem['runtime']
			if eRuntime is not None and len(eRuntime) > 0:
				info.Runtime = int(eRuntime)
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getRating(self, info, elem):
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
					return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None  

	def getGenre(self, info, elem):
		genre = u""
		try:
			genreList = elem['genres']
			for genreListItem in genreList:
				genre += genreListItem['name'] + u"|"
			if len(genre) > 0:
				info.Genres = genre[:len(genre) - 1] # Remove the last pipe
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getTranslated(self, elem):
		try:
			eLang = self.getElem(elem, "translated")
			if eLang is not None and eLang.data is not None and len(eLang.data) > 0:
				if eLang.data == "true":
					return True
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return False

	###############################################

	def getMovieByImdbID(self, info):
		if info.ImdbId == info.ImdbIdNull:
			printl(" <- None (info.ImdbId == info.ImdbIdNull)", self) 
			return None
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   u"en",	   url)
		result = WebGrabber.getJson(url)
		
		if result is None:
			printl(" <- None (result is None)", self) 
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
		printl(" <- None (eof)", self) 			
		return info


	def getMovie(self, info, lang):
		if info.TmDbId == info.TmDbIdNull:
			printl(" <- None (info.TmDbId == info.TmDbIdNull)", self) 
			return None
		
		lang = lang.lower()
		
		if lang == u"en":
			return info #en already parsed using getSerieByImdbID()
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   lang,		url)
		result = WebGrabber.getJson(url)
		
		if result is None:
			printl(" <- None (result is None)", self) 
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
		
		printl(" <- None (eof)", self)		
		return info

	def getArtByImdbId(self, info):
		if info.ImdbId == info.ImdbIdNull:
			printl(" <- None (info.ImdbId == info.ImdbIdNull)", self)
			return None
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   u"en",	   url)
		result = WebGrabber.getJson(url)
		
		if result is None:
			printl(" <- None (result is None)", self) 
			return None
		eMovie = json.loads(result)
		info.Poster = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/w300" + eMovie['poster_path']
		info.Backdrop = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/w1000" + eMovie['backdrop_path']
		
		if len(info.Poster) > 0 or len(info.Backdrop) > 0:
			return info
		
		printl(" <- None (eof)", self)
		return None
