# -*- coding: utf-8 -*-

import math
import os

from enigma import getDesktop
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText

from DataElement import DataElement
from DMC_Global import Showiframe
from DMC_View import DMC_View, localeInit, _

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

#localeInit()
#language.addCallback(localeInit)

def getViewClass():
	return DMC_ListView

class DMC_ListView(DMC_View):

	def __init__(self, session, libraryName, loadLibrary, playEntry):
		
		self.showiframe = Showiframe()
		
		DMC_View.__init__(self, session, libraryName, loadLibrary, playEntry, "PVMC_Series")
		
		self["poster"] 				= Pixmap()
		self["title"] 				= Label()
		if self.APILevel == 1:
			self["otitle"] 				= Label()
		self["tag"] 				= Label()
		self["shortDescription"] 	= Label()
		if self.APILevel == 1:
			self["director"] 			= Label()
			self["writer"] 				= Label()
		self["genre"] 				= Label()
		self["year"] 				= Label()
		self["runtime"] 			= Label()
		
		if self.APILevel >= 2:
			self["total"] = Label()
			self["current"] = Label()
		
		self["key_red"] = StaticText(_(" "))
		self["key_green"] = StaticText(_(" "))
		self["key_yellow"] = StaticText(_(" "))
		self["key_blue"] = StaticText(_("Toggle view"))
		
		try:
			from StillPicture import StillPicture
			self["backdrop"] = StillPicture(session)
			self.ShowStillPicture = True
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		self.postersize = ""
		if self.APILevel >= 3:
			dSize = getDesktop(0).size()
			if dSize.width() == 720 and dSize.height() == 576:
				self.postersize = "_110x214"
			elif dSize.width() == 1024 and dSize.height() == 576:
				self.postersize = "_156x214"
			elif dSize.width() == 1280 and dSize.height() == 720:
				self.postersize = "_195x267"
		
		for i in range(10):
			stars = "star" + str(i)
			printl("stars: " + stars, self)
			self[stars] = Pixmap()
			if self[stars].instance is not None:
				self[stars].instance.hide()
		
		for i in range(10):
			stars = "nostar" + str(i)
			printl("stars: " + stars, self)
			self[stars] = Pixmap()
		
		self.skinName = "PVMC_Series"

	def _refresh(self, selection, changeBackdrop):
		element = selection[1]
		if self.ShowStillPicture is True:
			if changeBackdrop is True:
				backdrop = config.plugins.pvmc.mediafolderpath.value + element["ArtId"] + "_backdrop.m1v"
				if os.access(backdrop, os.F_OK):
					self["backdrop"].setStillPicture(backdrop)
				else:
					self["backdrop"].setStillPictureToDefault()
		
		if self["poster"].instance is not None:
			poster = config.plugins.pvmc.mediafolderpath.value + element["ArtId"] + "_poster"
			if os.access(poster + self.postersize + ".png", os.F_OK):
				self["poster"].instance.setPixmapFromFile(poster + self.postersize + ".png")
			#Fallback for old skins
			elif len(self.postersize) == 0 and os.access(poster + "_156x214.png", os.F_OK):
				self["poster"].instance.setPixmapFromFile(poster + "_156x214.png")
			else:
				self["poster"].instance.setPixmapFromFile(config.plugins.pvmc.mediafolderpath.value + "defaultposter" + self.postersize + ".png")
		
		self.setText("title", selection[0])
		if self.APILevel == 1:
			self.setText("otitle", "---") #self.moviedb[selection[1]]["OTitle"])
		self.setText("tag", element["Tag"], True)
		
		self.setText("shortDescription", element["Plot"], what=_("Overview"))
		
		if self.APILevel == 1:
			if selection[1].has_key("Directors"):
				self.setText("director", element["Directors"])
			if selection[1].has_key("Writers"):
				self.setText("writer", element["Writers"])
		
		self.setText("genre", element["Genres"].replace('|', " / "), what=_("Genre"))
		#self.setText("year", str(element["Year"]))
		date = str(element["Year"])
		if element.has_key("Month") and element.has_key("Day"):
			if element["Month"] > 0 and element["Day"] > 0:
				date = "%04d-%02d-%02d" % (element["Year"], element["Month"], element["Day"], )
		self.setText("year", date)
		self.setText("runtime", str(element["Runtime"]) + ' ' + _("min"))
		
		for i in range(int(element["Popularity"])):
			if self["star" + str(i)].instance is not None:
				self["star" + str(i)].instance.show()
		
		for i in range(10 - int(element["Popularity"])):
			if self["star" + str(9 - i)].instance is not None:
				self["star" + str(9 - i)].instance.hide()
		
		if self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			#print "itemsPerPage", itemsPerPage
			pageTotal = int(math.ceil((itemsTotal / itemsPerPage) + 0.5))
			pageCurrent = int(math.ceil((self["listview"].getIndex() / itemsPerPage) + 0.5))
			self.setText("total", _("Total:") + ' ' + str(itemsTotal))
			self.setText("current", _("Pages:") + ' ' + str(pageCurrent) + "/" + str(pageTotal))

	def close(self, arg=None):
		self.showiframe.finishStillPicture()
		super(DMC_ListView, self).close(arg)

	def playEntry(self, entry):
		self.showiframe.finishStillPicture()
		super(DMC_ListView, self).playEntry(entry)

	def onKeyUp(self):
		self.onPreviousEntry()

	def onKeyUpQuick(self):
		self.onPreviousEntryQuick()

	def onKeyDown(self):
		self.onNextEntry()

	def onKeyDownQuick(self):
		self.onNextEntryQuick()

	def onKeyLeft(self):
		self.onPreviousPage()

	def onKeyRight(self):
		self.onNextPage()
