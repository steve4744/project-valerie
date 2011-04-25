# -*- coding: utf-8 -*-

import codecs

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

##
# Converts RAW strings to UTF-8 strings
# @param rawString: The RAW string 
# @return: The UTF-8 string or None if conversion failed
def stringToUtf8(rawString):
	utf8String = None
	if rawString is not None:
		try:
			utf8String = unicode(rawString, "utf-8")
		except UnicodeDecodeError, ex:
			printl("Conversion to utf-8 failed, trying different approach! Ex: " + str(ex), __name__)
			try:
				printl("type(rawString): " + str(type(rawString)), __name__)
				utf8String = unicode(rawString, "latin-1")
			except UnicodeDecodeError, ex2:
				printl("Conversion to utf-8 failed!!! Ignoring Ex: " + str(ex2), __name__)
				utf8String = None
		
		except Exception, ex:
			printl("Conversion to utf-8 failed!!! Something unexpected happened Ex: " + str(ex), __name__)
			utf8String = None
	
	return utf8String

##
# Converts UTF-8 strings to Latin-1 strings
# @param utfString: The UTF-8 string 
# @return: The Latin-1 string or an empty string if conversion failed
def utf8ToLatin(utfString):
	latinString = None
	if utfString is not None:
		try:
			latinString = utfString.encode('latin-1')
		except Exception, ex:
			printl("Conversion to latin failed, trying different approach! Ex: " + str(ex), __name__)
			try:
				printl("type(rawString): " + str(type(utfString)), __name__)
				latinString = utfString.encode('utf-8')
			except UnicodeDecodeError, ex2:
				printl("Conversion to latin failed!! Ex: " + str(ex2), __name__)
				latinString = None
	
	if latinString is None:
		latinString = " "
	
	return latinString

class Utf8():
	fd = None
	
	def __init__(self, file, arg):
		self.open(file, arg)
		
	def open(self, file, arg):
		try:
			try:
				self.fd = codecs.open(file, arg, "utf-8")
				return True
			except Exception, ex:
				printl("Exception: " + str(ex), self)
			
			self.fd = codecs.open(utf8ToLatin(file), arg, "utf-8")
			return True
		except Exception, ex:
			printl("Exception: " + str(ex), self)
			self.fd = None
			return False
		self.fd = None
		return False

	def close(self):
		if self.fd is not None:
			self.fd.close()

	def write(self, text):
		if self.fd is not None:
			try:
				self.fd.write(text)
			except Exception, ex:
				printl("Exception: " + str(ex), self)

	def read(self):
		if self.fd is not None:
			try:
				rtv = self.fd.read()[:-1]
				return rtv
			except Exception, ex:
				printl("Exception: " + str(ex), self)
				return None
		return None
