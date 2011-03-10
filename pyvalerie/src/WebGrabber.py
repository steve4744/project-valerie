# -*- coding: utf-8 -*-

import os
import re
import socket
import sys, traceback
from   sys import version_info
import urllib
import urllib2
import urlparse
import xml.dom.minidom as minidom

from   HtmlEncoding import decode_htmlentities
import Utf8

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

baseDir = "/tmp/valerie"
cacheDir = baseDir + "/cache"
downloadDir = "/hdd/valerie/media"

RETRIES = 5

def url_fix(s):
	scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
	path = urllib.quote(path, '/%')
	qs = urllib.quote_plus(qs, ':&=')
	#print "qs", qs #%26
	qs = qs.replace(u"&", u"%26")
	return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def folderSize(folder):
	folder_size = 0
	for (path, dirs, files) in os.walk(folder):
		for file in files:
			filename = os.path.join(path, file)
			folder_size += os.path.getsize(filename)
	return folder_size/(1024*1024.0)

def freeSpace(folder):
	s = os.statvfs(folder)
	return (s.f_bavail * s.f_frsize)/(1024*1024.0)

def checkCache(url):
	try:
		cacheFile = re.sub(r'\W', "", url).strip()
		cacheFileName = cacheDir + u"/" + cacheFile + u".cache"
		rtv = None
		if os.path.isfile(Utf8.utf8ToLatin(cacheFileName)):
			if os.path.getsize(Utf8.utf8ToLatin(cacheFileName)) == 0:
				os.remove(Utf8.utf8ToLatin(cacheFileName))
				return rtv
			f = Utf8.Utf8(cacheDir + u"/" + cacheFile + u".cache", "r")
			rtv = f.read()
			f.close()
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__)
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__)
	
	return rtv

def createCacheFolder():
	try: 
		os.makedirs(baseDir)
	except OSError, e:
		pass
	
	try: 
		os.makedirs(cacheDir)
	except OSError, e:
		pass

def addCache(url, text):
	
	# this line should be moved to a more suitable place
	createCacheFolder()
	
	try:
		if folderSize(cacheDir) > 4.0 or freeSpace(cacheDir) < 2.0: #10mb
			for f in os.listdir(cacheDir):
				file = os.path.join(cacheDir, f)
				printl("RM: " + str(file), __name__)
				os.remove(file)
		
		cacheFile = re.sub(r'\W', "", url).strip()
		cacheFileName = cacheDir + u"/" + cacheFile + u".cache"
		if text is not None and len(text) > 0:
			f = Utf8.Utf8(cacheFileName, "w")
			f.write(text)
			f.close
			
			if os.path.getsize(Utf8.utf8ToLatin(cacheFileName)) == 0:
				os.remove(Utf8.utf8ToLatin(cacheFileName))
			
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__)
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__)

def getXml(url, rawXml = None):
	try:
		if rawXml is None:
			rawXml = getText(url) 
		decodedXml = None
		try:
			if rawXml is not None:
				try:
					decodedXml = minidom.parseString(rawXml.encode( "utf-8" ))
				except Exception, ex:
					printl("minidom.parseString as utf-8 failed, retrieing as latin-1. Ex: " + str(ex), __name__)
					decodedXml = minidom.parseString(rawXml)
		except Exception, ex:
			printl("minidom.parseString as utf-8 and latin-1 failed, ignoring. Ex: " + str(ex), __name__)
			printl("URL: " + str(Utf8.utf8ToLatin(url)), __name__)
			#printl("rawXml: <" + str(type(rawXml)) + "> " + str(rawXml), __name__)
			printl("<" + str(type(ex)) + "> Ex: " + str(ex), __name__)
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__)
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__)
	
	return decodedXml

def getHtml(url):
	try:
		rawHtml = getText(url) 
		decodedHtml = None
		if rawHtml is not None:
			decodedHtml = decode_htmlentities(rawHtml)
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__)
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__)
	
	return decodedHtml

def getText(url): 
	try:
		utfPage = checkCache(url)
		if utfPage is None:
			for i in range(RETRIES):
				printl("-> (" + str(i) + ") " + str(Utf8.utf8ToLatin(url)), __name__)
				page = None
				kwargs = {}
				try:
					opener = urllib2.build_opener()
					opener.addheaders = [('User-agent', 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.7.62 Version/11.01')]
					#opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.8.1.6) Gecko/20070723 Iceweasel/2.0.0.6 (Debian-2.0.0.6-0etch1)')]
					if version_info[1] >= 6:
						page = opener.open(url_fix(Utf8.utf8ToLatin(url)), timeout=10)
					else:
						socket.setdefaulttimeout(10)
						page = opener.open(url_fix(Utf8.utf8ToLatin(url)))
				
				except IOError, ex:
					printl("IOError: " +  str(ex), __name__)
					continue
				
				if page is not None:
					rawPage = page.read()
					contenttype = page.headers['Content-type']
					print contenttype
					if contenttype.find("charset=") >= 0:
						encoding = page.headers['Content-type'].split('charset=')[1] # iso-8859-1
						utfPage = rawPage.decode(encoding).encode('utf-8')
					else:
						utfPage = Utf8.stringToUtf8(rawPage)
					
					addCache(url, utfPage)
					break
		
		printl("<- " + str(type(utfPage)) + " " + str(Utf8.utf8ToLatin(url)), __name__)
		return utfPage
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__)
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__)
	
	return u""

def getFile(url, name, retry=3):
	try:
		localFilename = downloadDir + "/" + name
		url = url.strip() # Just to be on the save side
		if os.path.isfile(Utf8.utf8ToLatin(localFilename)) is False:
			for i in range(retry):
				try:
					page = urllib2.urlopen(url_fix(Utf8.utf8ToLatin(url)))
					f = open(Utf8.utf8ToLatin(localFilename), 'wb')
					f.write(page.read())
					f.close()
					break
				except Exception, ex:
					printl("File download failed. Ex: " + str(ex), __name__)
					printl("Name: " + str(Utf8.utf8ToLatin(name)), __name__)
					printl("Url: " + str(Utf8.utf8ToLatin(url)), __name__)
					printl("type(ex): " + str(type(ex)), __name__)
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__)
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__)
	
	return
