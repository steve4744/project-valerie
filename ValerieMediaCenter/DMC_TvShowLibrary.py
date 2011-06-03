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

class DMC_TvShowLibrary(DMC_Library):

    def __init__(self, session):
        self.manager = Manager()
        DMC_Library.__init__(self, session, "tv shows")

    ###
    # Return Value is expected to be:
    # (libraryArray, onEnterPrimaryKeys, onLeavePrimaryKeys, onLeaveSelectEntry
    def loadLibrary(self, primaryKeyValuePair):
        
        # Diplay all TVShows
        if primaryKeyValuePair is None:
            parsedLibrary = []
            library = self.manager.getAll(Manager.TVSHOWS)
            
            for tvshow in library:
                d = {}
                
                d["ArtId"] = utf8ToLatin(tvshow.TheTvDbId)
                
                d["ImdbId"]  = utf8ToLatin(tvshow.ImdbId)
                d["TheTvDbId"] = utf8ToLatin(tvshow.TheTvDbId)
                d["Title"]   = "  " + utf8ToLatin(tvshow.Title)
                d["Tag"]     = utf8ToLatin(tvshow.Tag)
                d["Year"]    = tvshow.Year
                d["Month"]   = tvshow.Month
                d["Day"]     = tvshow.Day
                d["Plot"]    = utf8ToLatin(tvshow.Plot)
                d["Runtime"] = tvshow.Runtime
                d["Popularity"] = tvshow.Popularity
                d["Genres"]  = utf8ToLatin(tvshow.Genres)
                
                parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50"))
            sort = (("Title", None, False), ("Popularity", "Popularity", True), )
            return (parsedLibrary, ("TheTvDbId", ), None, None, sort)
        
        # Display the Episodes Menu
        elif primaryKeyValuePair.has_key("TheTvDbId") and primaryKeyValuePair.has_key("Season"):
            parsedLibrary = []
            
            tvshow = self.manager.getElementByUsingPrimaryKey(Manager.TVSHOWS, \
                dict({'thetvdbid': primaryKeyValuePair["TheTvDbId"]}))
            
            library = self.manager.getAll(Manager.TVSHOWSEPISODES, primaryKeyValuePair["TheTvDbId"])
            
            for episode in library:
                if episode.Season == primaryKeyValuePair["Season"]:
                    d = {}
                    
                    d["ArtId"] = utf8ToLatin(tvshow.TheTvDbId)
                    
                    d["ImdbId"]  = utf8ToLatin(tvshow.ImdbId)
                    d["TheTvDbId"] = utf8ToLatin(episode.TheTvDbId)
                    d["Tag"]     = utf8ToLatin(tvshow.Tag)
                    d["Title"]   = "  %dx%02d: %s" % (episode.Season, episode.Episode, utf8ToLatin(episode.Title), )
                    d["Year"]    = episode.Year
                    d["Month"]   = episode.Month
                    d["Day"]     = episode.Day
                    d["Path"]    = utf8ToLatin(episode.Path + "/" + episode.Filename + "." + episode.Extension)
                    if self.checkFileCreationDate:
                        try:
                            d["Creation"] = os.stat(d["Path"]).st_mtime
                        except Exception, ex:
                            printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
                            d["Creation"] = 0
                    d["Season"]  = episode.Season
                    d["Episode"] = episode.Episode
                    d["Plot"]    = utf8ToLatin(episode.Plot)
                    d["Runtime"] = episode.Runtime
                    d["Popularity"] = episode.Popularity
                    d["Genres"]  = utf8ToLatin(episode.Genres)
                    d["Resolution"]  = utf8ToLatin(episode.Resolution)
                    d["Sound"]  = utf8ToLatin(episode.Sound)
                    
                    parsedLibrary.append((d["Title"], d, episode.Season * 1000 + episode.Episode, "50"))
            sort = [("Title", None, False), ("Popularity", "Popularity", True), ]
            if self.checkFileCreationDate:
                sort.append(("File Creation", "Creation", True))
            return (parsedLibrary, ("play", "TheTvDbId", "Season", "Episode", ), dict({ \
                'TheTvDbId': episode.TheTvDbId, \
                }), primaryKeyValuePair, sort)
        
        # Display the Seasons Menu
        elif primaryKeyValuePair.has_key("TheTvDbId"):
            parsedLibrary = []
            tvshow = self.manager.getElementByUsingPrimaryKey(Manager.TVSHOWS, \
                dict({'thetvdbid': primaryKeyValuePair["TheTvDbId"]}))
            d = {}
            
            d["ArtId"] = utf8ToLatin(tvshow.TheTvDbId)
            
            d["ImdbId"]  = utf8ToLatin(tvshow.ImdbId)
            d["TheTvDbId"] = utf8ToLatin(tvshow.TheTvDbId)
            d["Tag"]     = utf8ToLatin(tvshow.Tag)
            d["Year"]    = tvshow.Year
            d["Month"]   = tvshow.Month
            d["Day"]     = tvshow.Day
            d["Plot"]    = utf8ToLatin(tvshow.Plot)
            d["Runtime"] = tvshow.Runtime
            d["Popularity"] = tvshow.Popularity
            d["Genres"]  = utf8ToLatin(tvshow.Genres)
            library = self.manager.getAll(Manager.TVSHOWSEPISODES, primaryKeyValuePair["TheTvDbId"])
            
            seasons = []
            for entry in library:
                season = entry.__dict__["Season"]
                if season not in seasons:
                    seasons.append(season)
                    s = d.copy()
                    s["Title"]  = "  Season %2d" % (season, )
                    s["Season"] = season
                    parsedLibrary.append((s["Title"], s, season, "50"))
            sort = (("Title", None, False), )
            return (parsedLibrary, ("TheTvDbId", "Season", ), None, primaryKeyValuePair, sort)
        return None

    def getPlaybackList(self, entry):
        playbackList = []
        
        primaryKeyValuePair = {}
        primaryKeyValuePair["TheTvDbId"] = entry["TheTvDbId"]
        primaryKeyValuePair["Season"] = entry["Season"]
        library = self.loadLibrary(primaryKeyValuePair)[0]
        
        playbackList.append( (entry["Path"], entry["Title"], entry, ))
        nextEpisode = entry["Episode"] + 1
        
        found = True
        while found is True:
            found = False
            for episode in library:
                episodeDict = episode[1]
                if episodeDict["Episode"] == nextEpisode:
                    playbackList.append( (episodeDict["Path"], episodeDict["Title"], episodeDict, ))
                    nextEpisode += 1
                    found = True
                    break
        
        return playbackList

    def buildInfoPlaybackArgs(self, entry):
        args = {}
        args["title"]   = entry["Title"]
        args["year"]    = entry["Year"]
        args["thetvdb"] = entry["TheTvDbId"]
        args["season"]  = entry["Season"]
        args["episode"] = entry["Episode"]
        args["type"]    = "tvshow"
        return args

registerPlugin(Plugin(name=_("TV Shows"), start=DMC_TvShowLibrary, where=Plugin.MENU_VIDEOS))

