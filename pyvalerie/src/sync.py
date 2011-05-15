# -*- coding: utf-8 -*-

import os
from   os import environ
import sys
from   threading import Thread
import time

from enigma import getDesktop
from   Components.Language import language
import gettext
from   Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE

from   Arts import Arts
import Blacklist
import Config
from   Database import Database
import DirectoryScanner
from   FailedEntry import FailedEntry
from   GoogleProvider import GoogleProvider
from   LocalImdbProvider import LocalImdbProvider
import MediaInfo
from   MobileImdbComProvider import MobileImdbComProvider
import replace
from   TheMovieDbProvider import TheMovieDbProvider
from   TheTvDbProvider import TheTvDbProvider
import Utf8
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

def localeInit():
	lang = language.getLanguage()
	environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ProjectValerie", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ProjectValerie/locale/"))

def _(txt):
	t = gettext.dgettext("ProjectValerie", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)

def checkDefaults():
	
	try:
		printl("Check "+"/tmp/valerie", __name__)
		os.makedirs("/tmp/valerie") 
	except OSError, e:
		printl("\t- OK", __name__)
	else:
		printl("\t- Created", __name__)
	try: 
		printl("Check "+"/tmp/valerie/cache", __name__)
		os.makedirs("/tmp/valerie/cache") 
	except OSError, e:
		printl("\t- OK", __name__)
	else:
		printl("\t- Created", __name__)
	
	try: 
		printl("Check "+"/hdd/valerie", __name__)
		os.makedirs("/hdd/valerie") 
	except OSError, e:
		printl("\t- OK", __name__)
	else:
		printl("\t- Created", __name__)
	
	try: 
		printl("Check "+"/hdd/valerie/dreamscene", __name__)
		os.makedirs("/hdd/valerie/dreamscene") 
	except OSError, e:
		printl("\t- OK", __name__)
	else:
		printl("\t- Created", __name__)
	
	try: 
		printl("Check "+"/tmp/valerie/cache", __name__)
		os.makedirs("/tmp/valerie/cache") 
	except OSError, e:
		printl("\t- OK", __name__)
	else:
		printl("\t- Created", __name__)
	
	try: 
		printl("Check "+"/hdd/valerie/media", __name__)
		os.makedirs("/hdd/valerie/media")
	except OSError, e:
		printl("\t- OK", __name__)
	else:
		printl("\t- Created", __name__)
	
	DEFAULTURL = "http://project-valerie.googlecode.com/svn/trunk/default/"
	
	printl("Check "+"/hdd/valerie/media/*", __name__)
	if os.access("/hdd/valerie/media/defaultbackdrop.m1v", os.F_OK) is False:
		printl("Check defaultbackdrop.m1v - Missing -> Downloading", __name__)
		WebGrabber.getFile(DEFAULTURL+"defaultbackdrop.m1v", "defaultbackdrop.m1v")
	
	if os.access("/hdd/valerie/media/defaultposter.png", os.F_OK) is False:
		printl("Check defaultposter.png - Missing -> Downloading", __name__)
		WebGrabber.getFile(DEFAULTURL+"defaultposter.png", "defaultposter.png")
	if os.access("/hdd/valerie/media/defaultposter_110x214.png", os.F_OK) is False:
		printl("Check defaultposter_110x214.png - Missing -> Downloading", __name__)
		WebGrabber.getFile(DEFAULTURL+"defaultposter_110x214.png", "defaultposter_110x214.png")
	if os.access("/hdd/valerie/media/defaultposter_156x214.png", os.F_OK) is False:
		printl("Check defaultposter_156x214.png - Missing -> Downloading", __name__)
		WebGrabber.getFile(DEFAULTURL+"defaultposter_156x214.png", "defaultposter_156x214.png")
	if os.access("/hdd/valerie/media/defaultposter_195x267.png", os.F_OK) is False:
		printl("Check defaultposter_195x267.png - Missing -> Downloading", __name__)
		WebGrabber.getFile(DEFAULTURL+"defaultposter_195x267.png", "defaultposter_195x267.png")
	
	try: 
		printl("Check "+"/hdd/valerie/episodes", __name__)
		os.makedirs("/hdd/valerie/episodes")
	except OSError, e:
		printl("\t- OK", __name__)
	else:
		printl("\t- Created", __name__)
	
	###
	
	try:
		printl("Check "+"/hdd/valerie/valerie.conf", __name__)
		if os.path.isfile("/hdd/valerie/valerie.conf") is False:
			printl("Check valerie.conf - Missing -> Downloading", __name__)
			WebGrabber.getFile(DEFAULTURL+"valerie.conf", "/hdd/valerie/valerie.conf")
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	try:
		printl("Check "+"/hdd/valerie/pre.conf", __name__)
		if os.path.isfile("/hdd/valerie/pre.conf") is False:
			printl("Check pre.conf - Missing -> Downloading", __name__)
			WebGrabber.getFile(DEFAULTURL+"pre.conf", "/hdd/valerie/pre.conf")
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	try:
		printl("Check "+"/hdd/valerie/post_movie.conf", __name__)
		if os.path.isfile("/hdd/valerie/post_movie.conf") is False:
			printl("Check post_movie.conf - Missing -> Downloading", __name__)
			WebGrabber.getFile(DEFAULTURL+"post_movie.conf", "/hdd/valerie/post_movie.conf")
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	try:
		printl("Check "+"/hdd/valerie/post_tv.conf", __name__)
		if os.path.isfile("/hdd/valerie/post_tv.conf") is False:
			printl("Check post_tv.conf - Missing -> Downloading", __name__)
			WebGrabber.getFile(DEFAULTURL+"post_tv.conf", "/hdd/valerie/post_tv.conf")
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	try:
		printl("Check "+"/hdd/valerie/paths.conf", __name__)
		if os.path.isfile("/hdd/valerie/paths.conf") is False:
			printl("Check paths.conf - Missing -> Downloading", __name__)
			WebGrabber.getFile(DEFAULTURL+"paths.conf", "/hdd/valerie/paths.conf")
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)

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
		self.output(_("Thread running"))

	def run(self):
		#reload(sys)
		#sys.setdefaultencoding( "latin-1" )
		#sys.setdefaultencoding( "utf-8" )
		
		self.output(_("Loading Config"))
		
		Config.load()
		
		self.output(_("Loading Database"))
		printl("Loading Database", self)
		start_time = time.time()
		db = Database().getInstance()
		#db.reload()
		db.clearFailed()
		if self.mode != self.FAST and Config.getBoolean("delete") is True:
			db.deleteMissingFiles()
		
		if self.mode != self.FAST:
			db.transformGenres()
		
		printl("Entries: " + str(db), self)
		elapsed_time = time.time() - start_time
		printl("Loading Database took: " + str(elapsed_time), self)
		
		self.output(_("Loading Replacements"))
		printl("Loading Replacements", self)
		replace.load()
		
		self.output(_("Loading Filesystem"))
		printl("Loading Filesystem", self)
		ds = DirectoryScanner.DirectoryScanner()
		ds.clear()
		if self.mode == self.FAST:
			ds.load()
		
		self.output(_("Searching for media files"))
		printl("Searching for media files", self)
		start_time = time.time()
		fconf = Utf8.Utf8("/hdd/valerie/paths.conf", "r")
		lines = fconf.read().split(u"\n")
		fconf.close()
		
		elementList = None
		
		if len(lines) > 1:
			filetypes = lines[0].strip().split('|')
			filetypes.append("ifo")
			filetypes.append("iso")
			self.output(_("Extensions:") + ' ' + str(filetypes))
			printl("Extensions: " + str(filetypes), self)
			
			for path in lines[1:]: 
				path = path.strip()
				
				p = path.split(u'|')
				path = p[0]
				if len(p) > 1:
					type = p[1]
				else:
					type = u"MOVIE_AND_TV"
				
				if os.path.isdir(path):
					ds.setDirectory(Utf8.utf8ToLatin(path))
					ds.listDirectory(filetypes, "(sample)|(VTS)|(^\\.)", type)
			elementList = ds.getFileList()
		
		elapsed_time = time.time() - start_time
		printl("Searching for media files took: " + str(elapsed_time), self)
		
		dSize = getDesktop(0).size()
		posterSize = Arts.posterResolution[0]
		if dSize.width() == 720 and dSize.height() == 576:
			posterSize = Arts.posterResolution[0]
		elif dSize.width() == 1024 and dSize.height() == 576:
			posterSize = Arts.posterResolution[1]
		elif dSize.width() == 1280 and dSize.height() == 720:
			posterSize = Arts.posterResolution[2]
		
		if elementList is None:
			self.output(_("Found") + ' ' + str(0) + ' ' + _("media files"))
			printl("Found 0 media files", self)
		else:
			self.output(_("Found") + ' ' + str(len(elementList)) + ' ' + _("media files"))
			printl("Found " + str(len(elementList)) + " media files", self)
			
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
				
				if ".AppleDouble" in path:
					continue
				
				if (filename + u"." + extension) in Blacklist.get():
					printl("File blacklisted", self)
					continue
				
				alreadyInDb = db.checkDuplicate(path, filename, extension)
				if alreadyInDb is not None:
					#self.output("Already in db [ " + Utf8.utf8ToLatin(filename) + " ]")
					#db.addFailed(FailedEntry(path, filename, extension, FailedEntry.DUPLICATE_FILE))
					
					if Arts().isMissing(alreadyInDb):
						#self.output("Downloading missing poster")
						tmp = None
						if alreadyInDb.isMovie:
							tmp = TheMovieDbProvider().getArtByImdbId(alreadyInDb)
						elif alreadyInDb.isSerie or alreadyInDb.isEpisode:
							tmp = TheTvDbProvider().getArtByTheTvDbId(alreadyInDb)
						
						if tmp is not None:
							Arts().download(tmp)
							
							if alreadyInDb.isMovie:
								self.info(str(alreadyInDb.ImdbId) + "_poster_" + posterSize + ".png", 
									"", "")
							elif alreadyInDb.isSerie or alreadyInDb.isEpisode:
								self.info(str(alreadyInDb.TheTvDbId) + "_poster_" + posterSize + ".png", 
									"", "")
					
					continue
				
				printl("#"*60, self)
				self.output("(" + str(i) + "/" + str(len(elementList))  + ")")
				printl("(" + str(i) + "/" + str(len(elementList))  + ")", self)
				printl("#"*6, self)
				self.output("  -> " + Utf8.utf8ToLatin(path) + "\n    " + Utf8.utf8ToLatin(filename) + "." + Utf8.utf8ToLatin(extension))
				printl("  -> " + Utf8.utf8ToLatin(path) + "\n    " + Utf8.utf8ToLatin(filename) + "." + Utf8.utf8ToLatin(extension), self)
				
				elementInfo = MediaInfo.MediaInfo(path, filename, extension)
				
				printl("TYPE: " + str(type), self)
				
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
					if tmp[0] is True and tmp[1] is None:
						# seems to be no tvshows so lets parse as movie
						elementInfo.isMovie = True
						elementInfo.isSerie = False
					elif tmp[0] is True:
						elementInfo = tmp
					searchStringSplitted = elementInfo.SearchString.split("::")
					if len(searchStringSplitted) >= 2:
						elementInfo.SearchString = searchStringSplitted[0];
				
				tmp = MobileImdbComProvider().getMoviesByTitle(elementInfo)
				if tmp is None:
					db.addFailed(FailedEntry(path, filename, extension, FailedEntry.UNKNOWN))
					continue
				elementInfo = tmp
				
				results = Sync().syncWithId(elementInfo)
				if results is not None:
					for result in results:
						if db.add(result):
							result.Title = self.encodeMe(result.Title)
							if result.isMovie:
								self.info(str(result.ImdbId) + "_poster_" + posterSize + ".png", 
									result.Title, result.Year)
								printl("my_title " + result.Title, self, "I")
							else:
								self.info(str(result.TheTvDbId) + "_poster_" + posterSize + ".png", 
									result.Title, result.Year)
								printl("my_title " + result.Title, self, "I")
						else:
							cause = db.getAddFailedCauseOf()
							db.addFailed(FailedEntry(path, filename, extension, FailedEntry.ALREADY_IN_DB,
								cause))
							printl("Title already in db", self, "W")
			
			self.output("(" + str(i) + "/" + str(len(elementList)) + ")")
			printl("(" + str(i) + "/" + str(len(elementList)) + ")", self)
			self.progress(i)
		
		self.output(_("Saving database"))
		printl("Saving database", self)
		db.save()
		
		self.output(_("Saving Filesystem"))
		printl("Saving Filesystem", self)
		ds.save()
		del ds
		del elementList[:]
		del db
		
		self.output(_("Done"))
		printl("Done", self)
		self.output("---------------------------------------------------")
		self.output(_("Press Exit / Back"))
		
		self.finished(True)

	def encodeMe (self, text):
		decodedText = None
		try:
			decodedText = text.encode( "utf-8", 'ignore' )
			printl("encoded utf-8")
			return decodedText
		except Exception, ex:
			try:
				decodedText = text.encode( "iso8859-1", 'ignore' )
				printl("encoded iso8859-1")
				return decodedText
			except Exception, ex:
				try:
					decodedText = text.decode("cp1252").encode("utf-8")
					printl("encoded cp1252")
					return decodedText
				except Exception, ex:
					printl("no enconding succeeded")
		return None

class Sync():
	def syncWithId(self, elementInfo):
		if elementInfo.isMovie:
			# Ask TheMovieDB for the local title and plot
			tmp = TheMovieDbProvider().getMovieByImdbID(elementInfo)
			if tmp is not None:
				elementInfo = tmp
			
			tmp = TheMovieDbProvider().getMovie(elementInfo, u"en")
			if tmp is not None:
				elementInfo = tmp
			
			userLang = Config.getString("local")
			if userLang != u"en":
				tmp = TheMovieDbProvider().getMovie(elementInfo, userLang)
				if tmp is not None:
					elementInfo = tmp
					elementInfo.LanguageOfPlot = userLang;
			
			if userLang != elementInfo.LanguageOfPlot:
				tmp = LocalImdbProvider().getMoviesByImdbID(elementInfo, userLang)
				if tmp is not None:
					elementInfo = tmp
					elementInfo.LanguageOfPlot = userLang;
			
			###
			
			tmp = TheMovieDbProvider().getArtByImdbId(elementInfo)
			if tmp is not None:
				elementInfo = tmp
				Arts().download(elementInfo)
				
			return (elementInfo, )
		
		elif elementInfo.isSerie:
			tmp = TheTvDbProvider().getSerieByImdbID(elementInfo)
			if tmp is not None:
				elementInfo = tmp
			
			tmp = TheTvDbProvider().getSerie(elementInfo, u"en")
			if tmp is not None:
				elementInfo = tmp
				
			userLang = Config.getString("local")
			if userLang != u"en":
				tmp = TheTvDbProvider().getSerie(elementInfo, userLang)
				if tmp is not None:
					elementInfo = tmp
					elementInfo.LanguageOfPlot = userLang;
					
			if userLang != elementInfo.LanguageOfPlot:
				tmp = LocalImdbProvider().getMoviesByImdbID(elementInfo, userLang)
				if tmp is not None:
					elementInfo = tmp
					elementInfo.LanguageOfPlot = userLang;
			###
			
			tmp = TheTvDbProvider().getArtByTheTvDbId(elementInfo)
			if tmp is not None:
				elementInfo = tmp
				Arts().download(elementInfo)
					
			elementInfoe = elementInfo.copy()
			
			elementInfoe.isSerie = False
			elementInfoe.isEpisode = True
			
			###
			
			tmp = TheTvDbProvider().getEpisode(elementInfoe, u"en")
			if tmp is not None:
				elementInfoe = tmp
			
			if userLang != u"en":
				tmp = TheTvDbProvider().getEpisode(elementInfoe, userLang)
				if tmp is not None:
					elementInfoe = tmp
					elementInfoe.LanguageOfPlot = userLang;
			
			if userLang != elementInfoe.LanguageOfPlot:
				tmp = LocalImdbProvider().getEpisodeByImdbID(elementInfoe, userLang)
				if tmp is not None:
					elementInfoe = tmp
					elementInfoe.LanguageOfPlot = userLang;
					
			return (elementInfo, elementInfoe)
		else:
			return None
