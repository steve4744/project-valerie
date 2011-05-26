# -*- coding: utf-8 -*-

from DMC_Library import DMC_Library
from Plugins.Extensions.ProjectValerieSync.Manager import Manager
from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

class DMC_MovieLibrary(DMC_Library):

    def __init__(self, session):
        self.manager = Manager()
        self.manager.start()
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
                d["Path"]    = utf8ToLatin(movie.Path + "/" + movie.Filename + "." + movie.Extension)
                d["Plot"]    = utf8ToLatin(movie.Plot)
                d["Runtime"] = movie.Runtime
                d["Popularity"] = movie.Popularity
                d["Genres"]  = movie.Genres
                
                parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50"))
            return (parsedLibrary, ("play"), None, None)
        return None

    def buildInfoPlaybackArgs(self, entry):
        args = {}
        args["title"]   = entry["Title"]
        args["year"]    = entry["Year"]
        args["imdbid"] = entry["ImdbId"]
        args["type"]    = "movie"
        return args

registerPlugin(Plugin(name=_("Movies (test)"), start=DMC_MovieLibrary, where=Plugin.MENU_VIDEOS))

