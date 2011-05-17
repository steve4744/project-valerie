# -*- coding: utf-8 -*-

#from DataElement import DataElement
#import 

import os
import time

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#from db_handler import db_handler
#from sqlite3 import dbapi2 as sqlite 

class databaseLayer(object):
    DB_TXT    = 1
    DB_TXD    = 2
    DB_PICKLE = 3
    DB_SQLITE = 4

    USE_DB_TYPE    = DB_TXT
    #USE_DB_VERSION = 0
    
    DB_PATH = "/hdd/valerie/"
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
    
    def getDBType():
        return self.USE_DB_TYPE
    
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
            #printl("Lines: " + str(linesLen), self)
            
            size = 11
            if int(version) >= 3:
                    size = 13
            else:
                    size = 11
            
            tmpGenres = [] # for speedup search
            
            for i in range(1, linesLen, size):
                if lines[i+0] == "EOF":
                        break
                d = {} 
                if int(version) >=3:
                        d["ImdbId"]     = lines[i+0]
                        d["Title"]      = lines[i+1]
                        d["Tag"]        = lines[i+2]
                        d["Year"]       = int(lines[i+3])
                        d["Month"]      = int(lines[i+4])
                        d["Day"]        = int(lines[i+5])
                        d["Path"]       = lines[i+6] + "/" + lines[i+7] + "." + lines[i+8]
                        d["Plot"]       = lines[i+9]
                        d["Runtime"]    = lines[i+10]
                        d["Popularity"] = lines[i+11]
                        d["Genres"]     = lines[i+12]
                else:
                        d["ImdbId"]    = lines[i+0]
                        d["Title"]     = lines[i+1]
                        d["Tag"]       = lines[i+2]
                        d["Year"]      = int(lines[i+3])
                        d["Path"] = lines[i+4] + "/" + lines[i+5] + "." + lines[i+6]
                        d["Plot"]       = lines[i+7]
                        d["Runtime"]    = lines[i+8]
                        d["Popularity"] = lines[i+9]
                        d["Genres"] = lines[i+10]
                
                try:
                        d["Creation"] = os.stat(d["Path"]).st_mtime
                except:
                        d["Creation"] = 0
                
                # deprecated
                d["Directors"] = ""
                d["Writers"]   = ""
                d["OTitle"]    = ""
                
                for genre in d["Genres"].split("|"):
                        if len(genre) > 0 and (genre) not in tmpGenres:
                                tmpGenres.append( genre )
                
                self.moviedb[d["ImdbId"]] = d
    
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

    ###########################################################################
    ##  SAVE  -  To use on ValeriaSync or on future options here
    ###########################################################################
    