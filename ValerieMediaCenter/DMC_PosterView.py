# -*- coding: utf-8 -*-

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
	return DMC_PosterView

class DMC_PosterView(DMC_View):

	def __init__(self, session, libraryName, loadLibrary, playEntry, select=None, sort=None):
		
		self.showiframe = Showiframe()
		
		DMC_View.__init__(self, session, libraryName, loadLibrary, playEntry, "PVMC_PosterView", select, sort)
		
		self["poster_-3"] = Pixmap()
		self["poster_-2"] = Pixmap()
		self["poster_-1"] = Pixmap()
		self["poster_0"]  = Pixmap()
		self["poster_+1"] = Pixmap()
		self["poster_+2"] = Pixmap()
		self["poster_+3"] = Pixmap()
		
		self["title"] = Label()
		
		self["key_red"] = StaticText(_(" "))
		self["key_green"] = StaticText(_("Sort: ") + _("Default"))
		self["key_yellow"] = StaticText(_(" "))
		self["key_blue"] = StaticText(_("View: ") + _("Poster-Flow")) #TODO: Name should be more dynamic
		
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
		
		self.skinName = "PVMC_PosterView"

	def _refresh(self, selection, changeBackdrop):
		element = selection[1]
		if self.ShowStillPicture is True:
			if changeBackdrop is True:
				backdrop = config.plugins.pvmc.mediafolderpath.value + element["ArtId"] + "_backdrop.m1v"
				if os.access(backdrop, os.F_OK):
					self["backdrop"].setStillPicture(backdrop)
				else:
					self["backdrop"].setStillPictureToDefault()
		
		self.setPoster("poster_0", element["ArtId"])
		
		if self.APILevel >= 2:
			currentIndex = self["listview"].getIndex()
			count = len(self.listViewList)
			for i in range(1,4): # 1, 2, 3
				if currentIndex >= i:
					self.setPoster("poster_-" + str(i), self.listViewList[currentIndex - i][1]["ArtId"])
				else:
					self["poster_-" + str(i)].hide()
				if currentIndex + i < count:
					self.setPoster("poster_+" + str(i), self.listViewList[currentIndex + i][1]["ArtId"])
				else:
					self["poster_+" + str(i)].hide()
		
		self.setText("title", selection[0])

	def setPoster(self, posterName, artId):
		if self[posterName].instance is not None:
			self[posterName].show()
			poster = config.plugins.pvmc.mediafolderpath.value + artId + "_poster"
			if os.access(poster + self.postersize + ".png", os.F_OK):
				self[posterName].instance.setPixmapFromFile(poster + self.postersize + ".png")
			else:
				self[posterName].instance.setPixmapFromFile(config.plugins.pvmc.mediafolderpath.value + \
					"defaultposter" + self.postersize + ".png")

	def close(self, arg=None):
		self.showiframe.finishStillPicture()
		super(DMC_PosterView, self).close(arg)

	def playEntry(self, entry):
		self.showiframe.finishStillPicture()
		super(DMC_PosterView, self).playEntry(entry)

	def sort(self):
		self["key_green"].setText(_("Sort: ") + _(self.activeSort[0]))
		super(DMC_PosterView, self).sort()

	def onKeyLeft(self):
		self.onPreviousEntry()

	def onKeyLeftQuick(self):
		self.onPreviousEntryQuick()

	def onKeyRight(self):
		self.onNextEntry()

	def onKeyRightQuick(self):
		self.onNextEntryQuick()

	def onKeyUp(self):
		self.onPreviousPage()

	def onKeyUpQuick(self):
		pass

	def onKeyDown(self):
		self.onNextPage()

	def onKeyDownQuick(self):
		pass
