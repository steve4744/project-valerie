# -*- coding: utf-8 -*-

#from DataElement import DataElement
#import 

import os
import time

from Components.config import config

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#from db_handler import db_handler
#from sqlite3 import dbapi2 as sqlite 

from Plugins.Extensions.ProjectValerieSync.MediaInfo import *
#------------------------------------------------------------------------------------------

class databaseLayer(object):
    DB_TXT    = 1
    DB_TXD    = 2
    DB_PICKLE = 3
    DB_SQLITE = 4

    USE_DB_TYPE    = DB_TXT
    #USE_DB_VERSION = 0
    
    DB_PATH = config.plugins.pvmc.configfolderpath.value
    DB_TXT_FILENAME_M = "movies.txt"
    DB_TXT_FILENAME_S = ".txt"
    DB_TXD_FILENAME_M = "movies.txd"
    DB_TXD_FILENAME_S = ".txd"
    DB_SQL_FILENAME   = "valerie.db"

    def __init__(self):
        printl("->", self)
        self.moviedb = {}
        self.AvailableGenresList = []
        
        if os.path.exists(self.DB_PATH + self.DB_SQL_FILENAME):
            self.sqlConnectionString = self.DB_PATH + self.DB_SQL_FILENAME        
            self.setDBType(self.DB_SQLITE)
            
        elif os.path.exists(self.DB_PATH + self.DB_TXD_FILENAME_M):
            self.setDBType(self.DB_TXD)
            
        elif os.path.exists(self.DB_PATH + self.DB_TXT_FILENAME_M):
            self.setDBType(self.DB_TXT)
            #self.setDBVersion(DB_TXD)
           
    
    def setDBType(self, version):
        self.USE_DB_TYPE = version
        printl("DB Type set to " + str(version))
      
    def getAvailGenres(self):
        return self.AvailableGenresList

    
    ###########################################################################
    ##  LOAD 
    ###########################################################################
    def loadMovies(self):
        printl("->", self)
        self.moviedb = {}

        if self.USE_DB_TYPE == self.DB_TXT:
            return self.loadMoviesTxt()
        elif self.USE_DB_TYPE == self.DB_TXD:
            return self.loadMoviesTxd()
        elif self.USE_DB_TYPE == self.DB_SQLITE:
            return self.loadMoviesSql()
        else:
            printl("No database file... ",self)
            #Let's Create it ??? :-)
            return (self.moviedb)

    def loadMoviesTxt(self):         
        printl("->", self)
        # TXT Not supported ????
        printl("<-", self)
        return (self.moviedb)
        
    def loadMoviesTxd(self):
        printl("->", self)
        start_time = time.time()  
        try:
            self.serieslist=[]
            db = open(self.DB_PATH + self.DB_TXD_FILENAME_M).read()[:-1]
            
            lines = db.split("\n")
            version = lines[0]
            linesLen = len(lines)
            printl("Lines: " + str(linesLen), self)
            
            if int(version) >= 3:
                    size = 13
            else:
                    size = 11
                    
            # Test for db errors
            if  (linesLen-2) % size != 0:
                printl("#"*30, self)
                printl("# ALERT - TXD Bad format", self)
                printl("#"*30, self)
                for i in range(1, linesLen, size):
                    if lines[i][:2] != "tt":
                        printl ("# Possible error at line: " + str(i), self)
                        break                                      
            else:
                printl("DB OK", self)

            
            tmpGenres = [] # for speedup search
            
            for i in range(1, linesLen, size):
                if lines[i+0] == "EOF":
                        break
		m = MediaInfo()
		m.importDefined(lines[i:i+size], version, True, False, False)
                self.add(m)
                #d = {} 
                #if int(version) >=3:
                #        d["ImdbId"]     = lines[i+0]
                #        d["Title"]      = lines[i+1]
                #        d["Tag"]        = lines[i+2]
                #        d["Year"]       = int(lines[i+3])
                #        d["Month"]      = int(lines[i+4])
                #        d["Day"]        = int(lines[i+5])
                #        d["Path"]       = lines[i+6] + "/" + lines[i+7] + "." + lines[i+8]
                #        d["Plot"]       = lines[i+9]
                #        d["Runtime"]    = lines[i+10]
                #        d["Popularity"] = lines[i+11]
                #        d["Genres"]     = lines[i+12]
                #else:
                #        d["ImdbId"]    = lines[i+0]
                #        d["Title"]     = lines[i+1]
                #        d["Tag"]       = lines[i+2]
                #        d["Year"]      = int(lines[i+3])
                #        d["Path"] = lines[i+4] + "/" + lines[i+5] + "." + lines[i+6]
                #        d["Plot"]       = lines[i+7]
                #        d["Runtime"]    = lines[i+8]
                #        d["Popularity"] = lines[i+9]
                #        d["Genres"] = lines[i+10]
                #
                #try:
                #        d["Creation"] = os.stat(d["Path"]).st_mtime
                #except:
                #        d["Creation"] = 0
                #
                ## deprecated
                #d["Directors"] = ""
                #d["Writers"]   = ""
                #d["OTitle"]    = ""
                
                for genre in m.Genres.split("|"):
                        if len(genre) > 0 and (genre) not in tmpGenres:
                                tmpGenres.append( genre )
                
                #self.moviedb[d["ImdbId"]] = d
    
            self.AvailableGenresList = []
            for genre in tmpGenres:
                self.AvailableGenresList.append((_(genre), genre))
            self.AvailableGenresList.sort()
            self.AvailableGenresList.insert(0,(_("All"), "all"))
        
        except OSError, ex: 
                printl("OSError: " + str(ex), self)
        except IOError, ex: 
                printl("IOError: " + str(ex), self)
        
        elapsed_time = time.time() - start_time
        printl("<- Took " + str(elapsed_time), self)
        return (self.moviedb)
        
    def loadMoviesSql(self):         
        printl("->", self)
        start_time = time.time()          
            
        # make connection 
        #connection = sqlite.connect(self.sqlConnectionString)

        # Let's make the SQL code here :-)
        # db = databaseHandler()
        # db."SELECT * FROM Media WHERE MediaType=1       
        # db."SELECT * FROM Genres WHERE GenreID IN (SELECT GenreID FROM Media_Genres WHERE MediaID=999999)

        elapsed_time = time.time() - start_time
        printl("<- Took " + str(elapsed_time), self)
        return (self.moviedb)

#################### FROM  SYNC
	##
	# Adds media files to the db-Memory
	# @param media: The media file
	# @return: False if file is already in db or movie already in db, else True 
    def add(self, media):
            # Checks if a tvshow is already in the db, if so then we dont have to readd it a second time
            #if media.isSerie:
            #        if media.RecordStatus == MediaInfo.REC_FROM_DB:
            #                serieKey = media.Id
            #        else:
            #                serieKey = media.TheTvDbId
            #        if self.dbSeries.has_key(serieKey) is False:
            #                self.dbSeries[serieKey] = media
            #                return True
            #        else:
            #                #self._addFailedCauseOf = self.dbSeries[media.TheTvDbId]
            #                #return False
            #                return True # We return true here cause this is not a failure but simply means that the tvshow already exists in the db
            #
            #media.Path = media.Path.replace("\\", "/")
            # Checks if the file is already in db
            #if self.checkDuplicate(media.Path, media.Filename, media.Extension):
                    # This should never happen, this means that the same file is already in the db
                    # But is a failure describtion here necessary ?
            #       return False
            
            #Not IS USE pth = media.Path + "/" + media.Filename + "." + media.Extension
            #self.duplicateDetector.append(pth)
            
            if media.isMovie:
                    if media.RecordStatus == MediaInfo.REC_FROM_DB:
                            movieKey = media.Id
                    else:
                            movieKey = media.ImdbId
                    if self.moviedb.has_key(movieKey) is False:
                            self.moviedb[movieKey] = media
                    else: 
                            self._addFailedCauseOf = self.moviedb[movieKey]
                            return False
            #elif media.isEpisode:
            #        if media.RecordStatus == MediaInfo.REC_FROM_DB:
            #                episodeKey = media.Id
            #        else:
            #                episodeKey = media.TheTvDbId			 
            #        if self.dbEpisodes.has_key(episodeKey) is False:
            #                self.dbEpisodes[episodeKey] = {}
            #        
            #        if self.dbEpisodes[episodeKey].has_key(media.Season) is False:
            #                self.dbEpisodes[episodeKey][media.Season] = {}
            #        
            #        if self.dbEpisodes[episodeKey][media.Season].has_key(media.Episode) is False:
            #                self.dbEpisodes[episodeKey][media.Season][media.Episode] = media
            #        else:
            #                self._addFailedCauseOf = self.dbEpisodes[episodeKey][media.Season][media.Episode]
            #                return False
            #return True
