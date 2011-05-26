# -*- coding: utf-8 -*-

from DMC_Library import DMC_Library
from Plugins.Extensions.ProjectValerieSync.Manager import Manager
from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

class DMC_TvShowLibrary(DMC_Library):

    def __init__(self, session):
        self.manager = Manager()
        self.manager.start()
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
                d["Genres"]  = tvshow.Genres
                
                parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50"))
            return (parsedLibrary, ("TheTvDbId", ), None, None)
        
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
                    d["Season"]  = episode.Season
                    d["Episode"] = episode.Episode
                    d["Plot"]    = utf8ToLatin(episode.Plot)
                    d["Runtime"] = episode.Runtime
                    d["Popularity"] = episode.Popularity
                    d["Genres"]  = episode.Genres
                    
                    parsedLibrary.append((d["Title"], d, episode.Season * 1000 + episode.Episode, "50"))
            return (parsedLibrary, ("play"), dict({ \
                'TheTvDbId': episode.TheTvDbId, \
                }), primaryKeyValuePair)
        
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
            d["Genres"]  = tvshow.Genres
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
            return (parsedLibrary, ("TheTvDbId", "Season"), None, primaryKeyValuePair)
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

registerPlugin(Plugin(name=_("TV Shows (test)"), start=DMC_TvShowLibrary, where=Plugin.MENU_VIDEOS))

