# -*- coding: utf-8 -*-

from threading import Thread

import sys
import os

import Config
import DirectoryScanner
import MediaInfo
from Arts import Arts
from ImdbProvider import ImdbProvider
from TheMovieDbProvider import TheMovieDbProvider
from TheTvDbProvider import TheTvDbProvider
from Database import Database
from WebGrabber import WebGrabber
import replace

class pyvalerie(Thread):
	def __init__ (self, output, progress, range, info):
		Thread.__init__(self)
		self.output = output
		self.progress = progress
		self.range = range
		self.info = info
		self.output("Thread running")
		
	def run(self):
		#reload(sys)
		#sys.setdefaultencoding( "latin-1" )
		#sys.setdefaultencoding( "utf-8" )
		
		self.output("Loading Config")
		
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
		
		if os.access("/hdd/valerie/media/defaultbackdrop.m1v", os.F_OK) is False:
			self.output("Check defaultbackdrop.m1v - Missing -> Downloading")
			WebGrabber().grabFile("http://project-valerie.googlecode.com/svn/trunk/pc/default/defaultbackdrop.m1v", "defaultbackdrop.m1v")
		if os.access("/hdd/valerie/media/defaultposter.png", os.F_OK) is False:
			self.output("Check defaultposter.png - Missing -> Downloading")
			WebGrabber().grabFile("http://project-valerie.googlecode.com/svn/trunk/pc/default/defaultposter.png", "defaultposter.png")
		
		try: 
			print("Check "+"/hdd/valerie/episodes")
			os.makedirs("/hdd/valerie/episodes")
		except OSError, e:
			print(" - OK\n")
		else:
			print(" - Created\n")
		
		Config.load()
		
		self.output("Loading Database")
		db = Database()
		db.reload()
		
		self.output("Loading Replacements")
		replace.load()
		
		# Check default config
		try:
			print("Check "+"/hdd/valerie/paths.conf")
			if os.path.isfile("/hdd/valerie/paths.conf") is False:
				self.output("Check paths.conf - Missing -> Downloading")
				WebGrabber().grabFile("http://project-valerie.googlecode.com/svn/trunk/pyvalerie/src/paths.conf", "../paths.conf")
				print(" - Created\n")
			else:
				print(" - OK\n")
		except Exception:
			print(" - ERROR\n")
			
		try:
			print("Check "+"/hdd/valerie/valerie.conf")
			if os.path.isfile("/hdd/valerie/valerie.conf") is False:
				self.output("Check valerie.conf - Missing -> Downloading")
				WebGrabber().grabFile("http://project-valerie.googlecode.com/svn/trunk/pyvalerie/src/valerie.conf", "../valerie.conf")
				print(" - Created\n")
			else:
				print(" - OK\n")
		except Exception:
			print(" - ERROR\n")
		
		try:
			print("Check "+"/hdd/valerie/pre.conf")
			if os.path.isfile("/hdd/valerie/pre.conf") is False:
				self.output("Check pre.conf - Missing -> Downloading")
				WebGrabber().grabFile("http://project-valerie.googlecode.com/svn/trunk/pyvalerie/src/pre.conf", "../pre.conf")
				print(" - Created\n")
			else:
				print(" - OK\n")
		except Exception:
			print(" - ERROR\n")
		
		try:
			print("Check "+"/hdd/valerie/post_movie.conf")
			if os.path.isfile("/hdd/valerie/post_movie.conf") is False:
				self.output("Check post_movie.conf - Missing -> Downloading")
				WebGrabber().grabFile("http://project-valerie.googlecode.com/svn/trunk/pyvalerie/src/post_movie.conf", "../post_movie.conf")
				print(" - Created\n")
			else:
				print(" - OK\n")
		except Exception:
			print(" - ERROR\n")
		
		try:
			print("Check "+"/hdd/valerie/post_tv.conf")
			if os.path.isfile("/hdd/valerie/post_tv.conf") is False:
				self.output("Check post_tv.conf - Missing -> Downloading")
				WebGrabber().grabFile("http://project-valerie.googlecode.com/svn/trunk/pyvalerie/src/post_tv.conf", "../post_tv.conf")
				print(" - Created\n")
			else:
				print(" - OK\n")
		except Exception:
			print(" - ERROR\n")
		
		self.output("Searching for media files")
		fconf = open("/hdd/valerie/paths.conf", "r")
		filetypes = fconf.readline().strip().split('|')
		self.output("Extensions: " + str(filetypes))
		print filetypes
		ds = None
		elementList = None
		for path in fconf.readlines(): 
			path = path.strip()
			
			if os.path.isdir(path):
				ds = DirectoryScanner.DirectoryScanner(path)
				elementList = ds.listDirectory(filetypes, "(sample)")
				del ds
		self.output("Found " + str(len(elementList)) + " media files")
		
		self.range(len(elementList))
		
		i = 0
		for element in elementList:
			self.output("(" + str(i) + "/" + str(len(elementList))  + ")")
			self.progress(i)
			i = i + 1
			try:
				path = unicode(element[0].replace("\\", "/"), "utf-8")
				filename = unicode(element[1], "utf-8")
				extension = unicode(element[2], "utf-8")
			except UnicodeDecodeError, ex:
				try:
					print type(element[0]), type(element[1]), type(element[2])
					path = unicode(element[0].replace("\\", "/"), "latin-1")
					filename = unicode(element[1], "latin-1")
					extension = unicode(element[2], "latin-1")
				except UnicodeDecodeError, ex2:
					print "Conversion to utf-8 failed!!!", ex2
					#continue
			
			if "RECYCLE.BIN" in path:
				continue
				
			if db.checkDuplicate(path, filename, extension):
				#self.output("Already in db [ " + filename.encode('latin-1') + "." + extension.encode('latin-1') + " ]")
				continue
			else:
				self.output("-> " + filename.encode('latin-1') + "." + extension.encode('latin-1'))
				
			elementInfo = MediaInfo.MediaInfo(path, filename, extension)
			elementInfo.parse()
			#print elementInfo
			
			elementInfo = ImdbProvider().getMovieByTitle(elementInfo)
			
			if elementInfo.isMovie:
				# Ask TheMovieDB for the local title and plot
				elementInfo = TheMovieDbProvider().getMovieByImdbID(elementInfo)
				elementInfo = TheMovieDbProvider().getArtByImdbId(elementInfo)
				Arts().download(elementInfo)
				db.add(elementInfo)
				self.info(str(elementInfo.ImdbId) + "_poster.png", elementInfo.Title, elementInfo.Year)
			elif elementInfo.isSerie:
				elementInfo = TheTvDbProvider().getSerieByImdbID(elementInfo)
				
				elementInfo = TheTvDbProvider().getArtByTheTvDbId(elementInfo)
				#print elementInfo
				db.add(elementInfo)
				
				elementInfoe = elementInfo.copy()
				
				elementInfoe.isSerie = False
				elementInfoe.isEpisode = True
				
				elementInfoe = TheTvDbProvider().getEpisodeByTheTvDbId(elementInfoe)
				#print elementInfoe
				db.add(elementInfoe)
				Arts().download(elementInfo)
				self.info(str(elementInfo.TheTvDbId) + "_poster.png", elementInfo.Title, elementInfo.Year)
				
			
			
		fconf.close()
		
		self.output("(" + str(i) + "/" + str(len(elementList)) + ")")
		self.progress(i)
		
		self.output("Saving database")
		db.save()
		
		del elementList[:]
		del db
		
		self.output("Done")
		self.output("---------------------")
		self.output("Press Exit / Back")
