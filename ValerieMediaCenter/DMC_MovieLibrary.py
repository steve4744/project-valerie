# -*- coding: utf-8 -*-

import os

from DMC_Library import DMC_Library

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

gAvailable = True

class DMC_MovieLibrary(DMC_Library):

    def __init__(self, session):
        printl ("->", self)
        global Manager
        if Manager is None:
            from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
            printl ("Manager Imported")
        
        self.manager = Manager()
        DMC_Library.__init__(self, session, "movies")

    ###
    # Return Value is expected to be:
    # (libraryArray, onEnterPrimaryKeys, onLeavePrimaryKeys, onLeaveSelectEntry
    def loadLibrary(self, primaryKeyValuePair, seenPng= None, unseenPng=None):
        global Manager
        global utf8ToLatin
        if utf8ToLatin is None:
            from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
        
        # Diplay all TVShows
        if primaryKeyValuePair is None:
            parsedLibrary = []
            #library = self.manager.get-All(Manager.MOVIES)
	    library = self.manager.getMoviesValues()
	    
            tmpAbc = []
            tmpGenres = []
            for movie in library:
                d = {}
                d["ArtBackdropId"] = utf8ToLatin(movie.ImdbId)
                d["ArtPosterId"] = d["ArtBackdropId"]
                
                d["ImdbId"]  = utf8ToLatin(movie.ImdbId)
                d["Title"]   = "  " + utf8ToLatin(movie.Title)
                if d["Title"][2].upper() not in tmpAbc:
                    tmpAbc.append(d["Title"][2].upper())
                d["Tag"]     = utf8ToLatin(movie.Tag)
                d["Year"]    = movie.Year
                d["Month"]   = movie.Month
                d["Day"]     = movie.Day
                # Yeah its a bit supersufficial as date is already in it
                # But will allow the view to sort the list
                # avoid crash if Null Values
                yy=movie.Year
                mm=movie.Month
                dd=movie.Day
                if yy is None:
                    yy=0
                if mm is None:
                    mm=0
                if dd is None:
                    dd=0
                d["Date"]    = yy*10000 + mm*100 + dd
                #d["Date"]    = movie.Year*10000 + movie.Month*100 + movie.Day
                d["Filename"] = utf8ToLatin(movie.Filename).lower()
                d["Path"]    = utf8ToLatin(movie.Path + "/" + movie.Filename + "." + movie.Extension)
                if self.checkFileCreationDate:
                    d["Creation"] = 0
                    try:
			d["Creation"] = os.stat(d["Path"]).st_mtime
                    except Exception, ex:
                        printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
                        d["Creation"] = 0
                d["Plot"]    = utf8ToLatin(movie.Plot)
                d["Runtime"] = movie.Runtime
                d["Popularity"] = movie.Popularity
                d["Genres"]  = utf8ToLatin(movie.Genres).split("|")
                for genre in d["Genres"]:
                    if genre not in tmpGenres:
                        tmpGenres.append(genre)
                d["Resolution"]  = utf8ToLatin(movie.Resolution)
                d["Sound"]  = utf8ToLatin(movie.Sound)
                
                if self.manager.isSeen({"ImdbId": d["ImdbId"]}):
                    image = seenPng
                else:
                    image = unseenPng
                
                parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50", image))
            sort = [("Title", None, False), ("Popularity", "Popularity", True), ("Aired", "Date", True), ]
            if self.checkFileCreationDate:
                sort.append(("File Creation", "Creation", True))
            
            sort.append(("Filename", "Filename", False))
            
            filter = [("All", (None, False), ("", )), ]
            if len(tmpGenres) > 0:
                tmpGenres.sort()
                filter.append(("Genre", ("Genres", True), tmpGenres))
            
            if len(tmpAbc) > 0:
                tmpAbc.sort()
                filter.append(("Abc", ("Title", False, 1), tmpAbc))
            
            return (parsedLibrary, ("play", "ImdbId", ), None, None, sort, filter)
        
        return None

    def buildInfoPlaybackArgs(self, entry):
        args = {}
        args["title"]   = entry["Title"]
        args["year"]    = entry["Year"]
        args["imdbid"]  = entry["ImdbId"]
        args["type"]    = "movie"
        return args

if gAvailable is True:
    registerPlugin(Plugin(name=_("Movies"), start=DMC_MovieLibrary, where=Plugin.MENU_VIDEOS))
