# -*- coding: utf-8 -*-

import os

from Screens.Screen import Screen

from DMC_View import DMC_View, getViews
from DMC_Player import PVMC_Player

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin

#------------------------------------------------------------------------------------------

class DMC_Library(Screen):

    checkFileCreationDate = True

    def __init__(self, session, libraryName):
        printl("", self, "D")
        Screen.__init__(self, session)
        self._session = session
        self._libraryName = libraryName
        
        self._views = getViews()
        self.currentViewIndex = 0
        
        self.onFirstExecBegin.append(self.showView)

    # Displays the selected View
    def showView(self, selection=None, sort=None, filter=None):
        printl("", self, "D")
        m = __import__(self._views[self.currentViewIndex][1], globals(), locals(), [], -1)
        print m
        print m.getViewClass()
        self._session.openWithCallback(self.onViewClosed, m.getViewClass(), self._libraryName, self.loadLibrary, self.playEntry, self._views[self.currentViewIndex], select=selection, sort=sort, filter=filter)

    # Called if View has closed, react on cause for example change to different view
    def onViewClosed(self, cause=None):
        printl("", self, "D")
        if cause is not None:
            if cause[0] == DMC_View.ON_CLOSED_CAUSE_CHANGE_VIEW:
                selection = None
                sort = None
                filter = None
                self.currentViewIndex += 1
                if len(self._views) <= self.currentViewIndex:
                    self.currentViewIndex = 0
                if len(cause) >= 2 and cause[1] is not None:
                    #self.currentViewIndex = cause[1]
                    selection = cause[1]
                if len(cause) >= 3 and cause[2] is not None:
                    sort = cause[2]
                if len(cause) >= 4 and cause[3] is not None:
                    filter = cause[3]
                if len(cause) >= 5 and cause[4] is not None:
                    for i in range(len(self._views)):
                        if cause[4][1] == self._views[i][1]:
                            self.currentViewIndex = i
                            break
                self.showView(selection, sort, filter)
            else:
                self.close()
        else:
            self.close()

    # prototype for library loading, is called by the view
    def loadLibrary(self, primaryKeyValuePair=None):
        #dict({'root': None})
        return []

    # starts playback, is called by the view
    def playEntry(self, entry):
        printl("", self, "D")
        playbackPath = entry["Path"]
        if playbackPath[0] == "/" and os.path.isfile(playbackPath) is False:
            return False
        else:
            self.notifyEntryPlaying(entry)
            
            isDVD, dvdFilelist, dvdDevice = self.checkIfDVD(playbackPath)
            if isDVD:
                self.playDVD(dvdDevice, dvdFilelist)
            else:
                self.playFile(entry)
            return True

    # tries to determin if media entry is a dvd
    def checkIfDVD(self, playbackPath):
        printl("", self, "D")
        isDVD = False
        dvdFilelist = [ ]
        dvdDevice = None
        
        if playbackPath.lower().endswith(u"ifo"): # DVD
            isDVD = True
            dvdFilelist.append(playbackPath.replace(u"/VIDEO_TS.IFO", "").strip())
        elif playbackPath.lower().endswith(u"iso"): # DVD
            isDVD = True
            dvdFilelist.append(playbackPath)
        return (isDVD, dvdFilelist, dvdDevice, )

    # playbacks a dvd by callinf dvdplayer plugin
    def playDVD(self, dvdDevice, dvdFilelist):
        printl("", self, "D")
        try:
            from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer
            # when iso -> filelist, when folder -> device
            self.session.openWithCallback(self.leaveMoviePlayer, DVDPlayer, \
                dvd_device = dvdDevice, dvd_filelist = dvdFilelist)
        except Exception, ex:
            printl("Exception: " + str(ex), self, "E")

    # playbacks a file by calling dmc_player
    def playFile(self, entry):
        printl("", self, "D")
        playbackList = self.getPlaybackList(entry)
        printl("playbackList: " + str(playbackList), self, "D")
        
        if len(playbackList) == 1:
            self.session.openWithCallback(self.leaveMoviePlayer, PVMC_Player, playbackList)
        elif len(playbackList) >= 2:
            self.session.openWithCallback(self.leaveMoviePlayer, PVMC_Player, playbackList, self.notifyNextEntry)

    # After calling this the view should auto reappear
    def leaveMoviePlayer(self): 
        self.notifyEntryStopped()
        
        self.session.nav.playService(None) 

    # prototype fore playbacklist creation
    def getPlaybackList(self, entry):
        printl("", self, "D")
        playbackList = []
        playbackList.append( (entry["Path"], entry["Title"], entry, ))
        return playbackList

    def buildInfoPlaybackArgs(self, entry):
        return {}

    # called on start of playback
    def notifyEntryPlaying(self, entry):
        printl("", self, "D")
        args = self.buildInfoPlaybackArgs(entry)
        args["status"]  = "playing"
        plugins = getPlugins(where=Plugin.INFO_PLAYBACK)
        for plugin in plugins:
            printl("plugin.name=" + str(plugin.name), self, "D")
            plugin.fnc(args)

    # called on end of playback
    def notifyEntryStopped(self):
        printl("", self, "D")
        args = {}
        args["status"] = "stopped"
        plugins = getPlugins(where=Plugin.INFO_PLAYBACK)
        for plugin in plugins:
            printl("plugin.name=" + str(plugin.name), self, "D")
            plugin.fnc(args)

    # called if the next entry in the playbacklist is being playbacked
    def notifyNextEntry(self, entry):
        printl("", self, "D")
        self.notifyEntryStopped()
        self.notifyEntryPlaying(entry)

