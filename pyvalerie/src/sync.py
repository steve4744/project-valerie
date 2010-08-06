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
			print("Check "+"/hdd/valerie/dl")
			os.makedirs("/hdd/valerie/dl")
		except OSError, e:
			print(" - OK\n")
		else:
			print(" - Created\n")
		
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
				f = open("/hdd/valerie/paths.conf", "wb")
				f.write("mkv|ts|avi|m2ts\n")
				f.write("/hdd\n")
				f.write("/autofs\n")
				f.write("/mnt\n")
				f.close()
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
			
			path = unicode(element[0].replace("\\", "/"), "utf-8")
			filename = unicode(element[1], "utf-8")
			extension = unicode(element[2], "utf-8")
			
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
