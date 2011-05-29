# -*- coding: utf-8 -*-

import os

from DMC_Library import DMC_Library
try:
	from Plugins.Extensions.ProjectValerieSync.Manager import Manager
	from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
except:
	from ..ProjectValerieSync.Manager import Manager
	from ..ProjectValerieSync.Utf8    import utf8ToLatin

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

class DMC_MovieLibrary(DMC_Library):

    def __init__(self, session):
        self.manager = Manager()
        DMC_Library.__init__(self, session, "movies")

    ###
    # Return Value is expected to be:
    # (libraryArray, onEnterPrimaryKeys, onLeavePrimaryKeys, onLeaveSelectEntry
    def loadLibrary(self, primaryKeyValuePair):
        # Diplay all TVShows
        if primaryKeyValuePair is None:
            parsedLibrary = []
            library = self.manager.getAll(Manager.MOVIES)
            
            for movie in library:
                d = {}
                
                d["ArtId"] = utf8ToLatin(movie.ImdbId)
                
                d["ImdbId"]  = utf8ToLatin(movie.ImdbId)
                d["Title"]   = "  " + utf8ToLatin(movie.Title)
                d["Tag"]     = utf8ToLatin(movie.Tag)
                d["Year"]    = movie.Year
                d["Month"]   = movie.Month
                d["Day"]     = movie.Day
                # Yeah its a bit supersufficial as date is already in it
                # But will allow the view to sort the list
                d["Date"]    = movie.Year*10000 + movie.Month*100 + movie.Day
                d["Path"]    = utf8ToLatin(movie.Path + "/" + movie.Filename + "." + movie.Extension)
                if self.checkFileCreationDate:
                    try:
                        d["Creation"] = os.stat(d["Path"]).st_mtime
                    except Exception, ex:
                        printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
                        d["Creation"] = 0
                d["Plot"]    = utf8ToLatin(movie.Plot)
                d["Runtime"] = movie.Runtime
                d["Popularity"] = movie.Popularity
                d["Genres"]  = utf8ToLatin(movie.Genres)
                d["Resolution"]  = utf8ToLatin(movie.Resolution)
                d["Sound"]  = utf8ToLatin(movie.Sound)
                
                parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50"))
            sort = [("Title", None, False), ("Popularity", "Popularity", True), ("Aired", "Date", True), ]
            if self.checkFileCreationDate:
                sort.append(("File Creation", "Creation", True))
            return (parsedLibrary, ("play", "ImdbId", ), None, None, sort)
        
        return None

    def buildInfoPlaybackArgs(self, entry):
        args = {}
        args["title"]   = entry["Title"]
        args["year"]    = entry["Year"]
        args["imdbid"] = entry["ImdbId"]
        args["type"]    = "movie"
        return args

registerPlugin(Plugin(name=_("Movies (test)"), start=DMC_MovieLibrary, where=Plugin.MENU_VIDEOS))

