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

#===============================================================================
# 
#===============================================================================
class Singleton:
	"""
	singlton config object
	"""
	__we_are_one = {}
	__valerieInstance = ""
	__logFileInstance = ""

	def __init__(self):
		#implement the borg patter (we are one)
		self.__dict__ = self.__we_are_one

	def getValerieInstance(self, value=None):
		'''with value you can set the singleton content'''
		if value:
			self.__valerieInstance = value
		return self.__valerieInstance
	
	def getLogFileInstance(self, value=None):
		'''with value you can set the singleton content'''
		if value:
			self.__logFileInstance = value
		return self.__logFileInstance