# -*- coding: utf-8 -*-

import cPickle as pickle
import os
import re

from Components.config import config

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class DirectoryScanner():

	directory = ""
	fileList = []
	
	folderList = {}
	
	FASTCRAWL_FILE = config.plugins.pvmc.configfolderpath.value + "fastcrawl.bin"
	isFastCrawlFileAvailable = False

	def __init__(self):
		self.clear()
		return None

	def clear(self):
		if len(self.fileList) > 0:
			del self.fileList[:]

	def load(self):
		if os.path.isfile(self.FASTCRAWL_FILE):
			self.isFastCrawlFileAvailable = True
			fd = open(self.FASTCRAWL_FILE, "rb")
			self.folderList = pickle.load(fd)
			fd.close()
		
		length = 0
		for key in self.folderList:
			length += len(self.folderList[key])
		printl("Folders: " + str(length), self)

	def save(self):
		fd = open(self.FASTCRAWL_FILE, "wb")
		pickle.dump(self.folderList, fd, 2) #pickle.HIGHEST_PROTOCOL)
		fd.close()

	def setDirectory(self, directory):
		self.directory = directory

	def getDirectory(self):
		return self.directory

	def getFileList(self):
		return self.fileList

	def listDirectory(self, fileExtList, fileIgnoreRegex, type):	 
		if self.directory not in self.folderList:
			self.folderList[self.directory] = {}
		
		if self.isFastCrawlFileAvailable is True and len(self.folderList[self.directory]) > 0:
			self._updateDirectory(self.directory, fileExtList, fileIgnoreRegex, type)
		else:
			self._listDirectory(self.directory, fileExtList, fileIgnoreRegex, type)

	def _updateDirectory(self, directory, fileExtList, fileIgnoreRegex, type):
		printl("directory=" + str(directory), self)
		allFolderKeys = self.folderList[directory].keys()
		for folderKey in allFolderKeys:
			try:
				mtime = os.path.getmtime(folderKey)
				# Also enter if is mounted directoy as these often have the wrong time
				if self.directory == folderKey or self.folderList[self.directory][folderKey] != mtime:
					printl("folderKey=" + str(folderKey) + " " + str(self.folderList[self.directory][folderKey]) + " " + str(mtime), self)
					self._directoryHasChanged(folderKey, fileExtList, fileIgnoreRegex, type)
					self.folderList[self.directory][folderKey] = mtime
			except Exception, ex:
				printl("Exception: " + str(ex), self)
				#del(self.folderList[directory][folderKey])

	def _directoryHasChanged(self, directory, fileExtList, fileIgnoreRegex, type):
		printl("directory=" + str(directory), self)
		try:
			for f in os.listdir(directory):
				file = os.path.join(directory, f)
				if os.path.isfile(file):
					# File is f and path is directory
					(shortname, extension) = self.filenameToTulpe(f)
					printl("shortname=" + str(shortname) + " extension=" + str(extension), self)
					if extension.lower() in fileExtList and fileIgnoreRegex is not None and re.search(fileIgnoreRegex, shortname) is None:
						self.fileList.append([directory, shortname, extension, type])
				
				elif os.path.isdir(file):
					# Check if this is a new folder
					#print file
					#print self.folderList[self.directory].keys()
					if file not in self.folderList[self.directory].keys():
						self.folderList[self.directory][file] = os.path.getmtime(file)
						self._listDirectory(file, fileExtList, fileIgnoreRegex, type)
					
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
	def _listDirectory(self, directory, fileExtList, fileIgnoreRegex, type, recursive=True):
		"get list of file info objects for files of particular extensions" 
		printl("directory=" + str(directory), self)

		if "RECYCLE.BIN" in directory:
			return

		try:
			for f in os.listdir(directory):
				file = os.path.join(directory, f)
				if os.path.isfile(file):
					# File is f and path is directory
					(shortname, extension) = self.filenameToTulpe(f)
					if extension.lower() in fileExtList and fileIgnoreRegex is not None and re.search(fileIgnoreRegex, shortname) is None:
						self.fileList.append([directory, shortname, extension, type])
				
				elif recursive is True and os.path.isdir(file):
					self.folderList[self.directory][directory] = os.path.getmtime(directory)
					self._listDirectory(file, fileExtList, fileIgnoreRegex, type)
		except Exception, ex:
			#import sys, traceback
			printl("Exception: " + str(ex), self)
			#exc_type, exc_value, exc_traceback = sys.exc_info()
			#print "*** print_tb:"
			#traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
			#print "*** print_exception:"
			#traceback.print_exception(exc_type, exc_value, exc_traceback,
			#						  limit=2, file=sys.stdout)
			#print "*** print_exc:"
			#traceback.print_exc()

	def fileToTulpe(self, file):
		(filepath, filename) = os.path.split(file)
		(shortname, extension) = self.filenameToTulpe(filename)
		return (filepath, shortname, extension)

	def filenameToTulpe(self, filename):
		(shortname, extension) = os.path.splitext(filename)
		return (shortname, extension[1:])
