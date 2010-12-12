# -*- coding: utf-8 -*-

from threading import Thread

import sys
import os

import Config
import DirectoryScanner
import MediaInfo
from Arts import Arts
from MobileImdbComProvider import MobileImdbComProvider
from LocalImdbProvider import LocalImdbProvider
from TheMovieDbProvider import TheMovieDbProvider
from TheTvDbProvider import TheTvDbProvider
from GoogleProvider import GoogleProvider
from Database import Database
import WebGrabber
import replace
import Utf8

def checkDefaults():
	try: 
		print("Check "+"/hdd/valerie")
		os.makedirs("/hdd/valerie") 
	except OSError, e:
		print(" - OK\n")
	else:
		print(" - Created\n")
	
	try: 
		print("Check "+"/hdd/valerie/cache")
		os.makedirs("/hdd/valerie/cache") 
	except OSError, e:
		print(" - OK\n")
	else:
		print(" - Created\n")
	
	try: 
		print("Check "+"/hdd/valerie/media")
		os.makedirs("/hdd/valerie/media")
	except OSError, e:
		print(" - OK\n")
	else:
		print(" - Created\n")
	
	DEFAULTURL = "http://project-valerie.googlecode.com/svn/trunk/default/"
	
	print("Check "+"/hdd/valerie/media")
	if os.access("/hdd/valerie/media/defaultbackdrop.m1v", os.F_OK) is False:
		print("Check defaultbackdrop.m1v - Missing -> Downloading")
		WebGrabber.getFile(DEFAULTURL+"defaultbackdrop.m1v", "../media/defaultbackdrop.m1v")
	if os.access("/hdd/valerie/media/defaultposter.png", os.F_OK) is False:
		print("Check defaultposter.png - Missing -> Downloading")
		WebGrabber.getFile(DEFAULTURL+"defaultposter.png", "../media/defaultposter.png")
	
	try: 
		print("Check "+"/hdd/valerie/episodes")
		os.makedirs("/hdd/valerie/episodes")
	except OSError, e:
		print(" - OK\n")
	else:
		print(" - Created\n")
	
	###
	
	try:
		print("Check "+"/hdd/valerie/valerie.conf")
		if os.path.isfile("/hdd/valerie/valerie.conf") is False:
			print("Check valerie.conf - Missing -> Downloading")
			WebGrabber.getFile(DEFAULTURL+"valerie.conf", "../valerie.conf")
			print(" - Created\n")
		else:
			print(" - OK\n")
	except Exception:
		print(" - ERROR\n")
		
		
	try:
		print("Check "+"/hdd/valerie/pre.conf")
		if os.path.isfile("/hdd/valerie/pre.conf") is False:
			print("Check pre.conf - Missing -> Downloading")
			WebGrabber.getFile(DEFAULTURL+"pre.conf", "../pre.conf")
			print(" - Created\n")
		else:
			print(" - OK\n")
	except Exception:
		print(" - ERROR\n")
	
	try:
		print("Check "+"/hdd/valerie/post_movie.conf")
		if os.path.isfile("/hdd/valerie/post_movie.conf") is False:
			print("Check post_movie.conf - Missing -> Downloading")
			WebGrabber.getFile(DEFAULTURL+"post_movie.conf", "../post_movie.conf")
			print(" - Created\n")
		else:
			print(" - OK\n")
	except Exception:
		print(" - ERROR\n")
	
	try:
		print("Check "+"/hdd/valerie/post_tv.conf")
		if os.path.isfile("/hdd/valerie/post_tv.conf") is False:
			print("Check post_tv.conf - Missing -> Downloading")
			WebGrabber.getFile(DEFAULTURL+"post_tv.conf", "../post_tv.conf")
			print(" - Created\n")
		else:
			print(" - OK\n")
	except Exception:
		print(" - ERROR\n")
	
	try:
		print("Check "+"/hdd/valerie/paths.conf")
		if os.path.isfile("/hdd/valerie/paths.conf") is False:
			print("Check paths.conf - Missing -> Downloading")
			WebGrabber.getFile(DEFAULTURL+"paths.conf", "../paths.conf")
			print(" - Created\n")
		else:
			print(" - OK\n")
	except Exception:
		print(" - ERROR\n")
	
import time
class pyvalerie(Thread):
	
	NORMAL = 0
	FAST = 1
	UPDATE = 2
	
	def __init__ (self, output, progress, range, info, finished, mode):
		Thread.__init__(self)
		self.output = output
		self.progress = progress
		self.range = range
		self.info = info
		self.finished = finished
		self.mode = mode
		self.output("Thread running")
		
	def run(self):
		#reload(sys)
		#sys.setdefaultencoding( "latin-1" )
		#sys.setdefaultencoding( "utf-8" )
		
		self.output("Loading Config")
		
		Config.load()
		
		self.output("Loading Database")
		start_time = time.time()
		db = Database()
		db.reload()
		print "  ", db
		elapsed_time = time.time() - start_time
		print "Took: ", elapsed_time
		
		#db.searchDeleted()
		#exit(0)
		
		self.output("Loading Replacements")
		replace.load()
		
		self.output("Loading Filesystem")
		ds = DirectoryScanner.DirectoryScanner()
		ds.clear()
		if self.mode == self.FAST:
			ds.load()
		
		self.output("Searching for media files")
		fconf = Utf8.Utf8("/hdd/valerie/paths.conf", "r")
		lines = fconf.read().split(u"\n")
		fconf.close()
		if len(lines) > 1:
			filetypes = lines[0].strip().split('|')
			self.output("    Extensions: " + str(filetypes))
			print filetypes
			
			start_time = time.time()
			
			elementList = None
			for path in lines[1:]: 
				path = path.strip()
				
				print "PATH: ", path
				
				p = path.split(u'|')
				path = p[0]
				if len(p) > 1:
					type = p[1]
				else:
					type = u"MOVIE_AND_TV"
				
				if os.path.isdir(path):
					ds.setDirectory(Utf8.utf8ToLatin(path))
					ds.listDirectory(filetypes, "(sample)", type)
			elementList = ds.getFileList()
			
			elapsed_time = time.time() - start_time
			print "Took: ", elapsed_time
			
			if elementList is None:
				self.output("Found " + str(0) + " media files")
			else:
				self.output("Found " + str(len(elementList)) + " media files")
				
				self.range(len(elementList))
				
				i = 0
				for element in elementList:
					i = i + 1
					self.progress(i)
					
					path      = Utf8.stringToUtf8(element[0]).replace("\\", "/")
					filename  = Utf8.stringToUtf8(element[1])
					extension = Utf8.stringToUtf8(element[2])
					type      = element[3]
					if path is None or filename is None or extension is None:
						continue
					
					if "RECYCLE.BIN" in path:
						continue
						
					if db.checkDuplicate(path, filename, extension):
						#self.output("Already in db [ " + Utf8.utf8ToLatin(filename) + " ]")
						continue
					
					self.output("(" + str(i) + "/" + str(len(elementList))  + ")")	
					print "-"*60	
					self.output("  -> " + Utf8.utf8ToLatin(path) + "\n    " + Utf8.utf8ToLatin(filename) + "." + Utf8.utf8ToLatin(extension))
						
					elementInfo = MediaInfo.MediaInfo(path, filename, extension)
					
					print "TYPE:", type
					
					if type == u"MOVIE":
						elementInfo.isMovie = True
						elementInfo.isSerie = False
					elif type == u"TV":
						elementInfo.isMovie = False
						elementInfo.isSerie = True
					
					result = elementInfo.parse()
					
					if result == False:
						continue
					
					if elementInfo.isSerie and elementInfo.isEnigma2MetaRecording:
						tmp = GoogleProvider().getSeasonAndEpisodeFromEpisodeName(elementInfo)
						if tmp is None:
							print "MobileImdbComProvider().getMoviesByTitle(elementInfo) returned None"
						else:
							elementInfo = tmp
							searchStringSplitted = elementInfo.SearchString.split("::")
							if len(searchStringSplitted) >= 2:
								elementInfo.SearchString = searchStringSplitted[0];
								
					#elementInfo = ImdbProvider().getMovieByTitle(elementInfo)
					tmp = MobileImdbComProvider().getMoviesByTitle(elementInfo)
					if tmp is None:
						print "MobileImdbComProvider().getMoviesByTitle(elementInfo) returned None"
						continue
					elementInfo = tmp
					
					if elementInfo.isMovie:
						# Ask TheMovieDB for the local title and plot
						tmp = TheMovieDbProvider().getMovieByImdbID(elementInfo)
						if tmp is None:
							print "TheMovieDbProvider().getMovieByImdbID(elementInfo) returned None"
						else:
							elementInfo = tmp

						tmp = TheMovieDbProvider().getMovie(elementInfo, u"en")
						if tmp is None:
							print "TheMovieDbProvider().getMovie(elementInfo, u\"en\") returned None"
						else:
							elementInfo = tmp

						userLang = Config.getString("local")
						if userLang != u"en":
							tmp = TheMovieDbProvider().getMovie(elementInfo, userLang)
							if tmp is None:
								print "TheMovieDbProvider().getMovie(elementInfo, userLang) returned None"
							else:
								elementInfo = tmp
								elementInfo.LanguageOfPlot = userLang;

						if userLang != elementInfo.LanguageOfPlot:
							tmp = LocalImdbProvider().getMoviesByImdbID(elementInfo, userLang)
							if tmp is None:
								print "LocalImdbProvider().getMoviesByImdbID(elementInfo, userLang) returned None"
							else:
								elementInfo = tmp
								elementInfo.LanguageOfPlot = userLang;
						
						###

						tmp = TheMovieDbProvider().getArtByImdbId(elementInfo)
						if tmp is None:
							print "TheMovieDbProvider().getArtByImdbId(elementInfo) returned None"
						else:
							elementInfo = tmp
							Arts().download(elementInfo)
							
						if db.add(elementInfo):
							self.info(str(elementInfo.ImdbId) + "_poster.png", 
									Utf8.utf8ToLatin(elementInfo.Title), elementInfo.Year)
						else:
							print "Title already in db"
					elif elementInfo.isSerie:
						tmp = TheTvDbProvider().getSerieByImdbID(elementInfo)
						if tmp is None:
							print "TheTvDbProvider().getSerieByImdbID(elementInfo) returned None"
						else:
							elementInfo = tmp
						
						tmp = TheTvDbProvider().getSerie(elementInfo, u"en")
						if tmp is None:
							print "TheTvDbProvider().getSerie(elementInfo, u\"en\") returned None"
						else:
							elementInfo = tmp
							
						userLang = Config.getString("local")
						if userLang != u"en":
							tmp = TheTvDbProvider().getSerie(elementInfo, userLang)
							if tmp is None:
								print "TheTvDbProvider().getSerie(elementInfo, userLang) returned None"
							else:
								elementInfo = tmp
								elementInfo.LanguageOfPlot = userLang;
								
						if userLang != elementInfo.LanguageOfPlot:
							tmp = LocalImdbProvider().getMoviesByImdbID(elementInfo, userLang)
							if tmp is None:
								print "LocalImdbProvider().getMoviesByImdbID(elementInfo, userLang) returned None"
							else:
								elementInfo = tmp
								elementInfo.LanguageOfPlot = userLang;
						###
														
						tmp = TheTvDbProvider().getArtByTheTvDbId(elementInfo)
						if tmp is None:
							print "TheTvDbProvider().getArtByTheTvDbId(elementInfo) returned None"
						else:
							elementInfo = tmp
							Arts().download(elementInfo)
						
						#print elementInfo
						db.add(elementInfo)
						
						elementInfoe = elementInfo.copy()
						
						elementInfoe.isSerie = False
						elementInfoe.isEpisode = True
						
						###
						
						tmp = TheTvDbProvider().getEpisode(elementInfoe, u"en")
						if tmp is None:
							print "TheTvDbProvider().getEpisode(elementInfoe, u\"en\") returned None"
						else:
							elementInfoe = tmp
						
						if userLang != u"en":
							tmp = TheTvDbProvider().getEpisode(elementInfoe, userLang)
							if tmp is None:
								print "TheTvDbProvider().getEpisode(elementInfoe, userLang) returned None"
							else:
								elementInfoe = tmp
								elementInfoe.LanguageOfPlot = userLang;
						
						if userLang != elementInfoe.LanguageOfPlot:
							tmp = LocalImdbProvider().getEpisodeByImdbID(elementInfoe, userLang)
							if tmp is None:
								print "LocalImdbProvider().getEpisodeByImdbID(elementInfoe, userLang) returned None"
							else:
								elementInfoe = tmp
								elementInfoe.LanguageOfPlot = userLang;
								
						###
						
						#print elementInfoe
						
						if db.add(elementInfoe):
							self.info(str(elementInfoe.TheTvDbId) + "_poster.png", 
									Utf8.utf8ToLatin(elementInfoe.Title), elementInfoe.Year)
						else:
							print "Title already in db"
				
				self.output("(" + str(i) + "/" + str(len(elementList)) + ")")
				self.progress(i)
			
			
		
		
		self.output("Saving database")
		db.save()
		
		self.output("Saving Filesystem")
		ds.save()
		del ds
			
		del elementList[:]
		del db
		
		self.output("Done")
		self.output("---------------------")
		self.output("Press Exit / Back")
		
		self.finished(True)
