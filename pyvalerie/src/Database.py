'''
Created on 15.07.2010

@author: i7
'''

import os
from datetime import date
from MediaInfo import MediaInfo
import Utf8
import Config

import time
import cPickle as pickle
#import pickle

import DirectoryScanner
from FailedEntry import FailedEntry

class Database(object):
    '''
    classdocs
    '''

    

    def __init__(self):
        '''
        Constructor
        '''
        self.dbMovies = {}
        self.dbSeries = {}
        self.dbEpisodes = {}
        
        self.dbFailed = []
        
        self.duplicateDetector = []
        
    def reload(self):
        self.dbMovies = {}
        self.dbSeries = {}
        self.dbEpisodes = {}
        
        self.dbFailed = []
        
        self.duplicateDetector = []
        
        self.load()
    
    def clearFailed(self):
        del self.dbFailed[:]
    
    def addFailed(self, entry):
        self.dbFailed.append(entry)
    
    def removeFailed(self, entry):
        if entry in self.dbFailed:
            self.dbFailed.remove(entry)
     
    def searchDeleted(self):
        for key in self.dbMovies:
            m = self.dbMovies[key]
            path = m.Path + u"/" + m.Filename + u"." + m.Extension
            if os.path.exists(Utf8.utf8ToLatin(path)) is False:
                print ":-( " + Utf8.utf8ToLatin(path)
        
        for key in self.dbSeries:
            if key in self.dbEpisodes:
                for season in self.dbEpisodes[key]:
                    for episode in self.dbEpisodes[key][season]:
                        m = self.dbEpisodes[key][season][episode]
                        path = m.Path + u"/" + m.Filename + u"." + m.Extension
                        if os.path.exists(Utf8.utf8ToLatin(path)) is False:
                            print ":-( " + Utf8.utf8ToLatin(path)
        
    ##
    # Checks if file is already in the db
    # @param path: utf-8 
    # @param filename: utf-8 
    # @param extension: utf-8 
    # @return: True if already in db, False if not
        
    def checkDuplicate(self, path, filename, extension):
        for key in self.dbMovies:
            if self.dbMovies[key].Path == path:
                if self.dbMovies[key].Filename == filename:
                    if self.dbMovies[key].Extension == extension:
                        return True
        
        for key in self.dbSeries:
            if key in self.dbEpisodes:
                for season in self.dbEpisodes[key]:
                    for episode in self.dbEpisodes[key][season]:
                        if self.dbEpisodes[key][season][episode].Path == path:
                            if self.dbEpisodes[key][season][episode].Filename == filename:
                                if self.dbEpisodes[key][season][episode].Extension == extension:
                                    return True
        return False
        
        #if pth in self.duplicateDetector:
        #    return True
        #else:
        #    return False
    
    def remove(self, media):
        if media.isMovie:
            if self.dbMovies.has_key(media.ImdbId) is True:
                del(self.dbMovies[media.ImdbId])
        elif media.isSerie:
            if self.dbSeries.has_key(media.TheTvDbId) is True:
                del(self.dbSeries[media.TheTvDbId])
        elif media.isEpisode:
            if self.dbEpisodes.has_key(media.TheTvDbId) is True:
                if self.dbEpisodes[media.TheTvDbId].has_key(media.Season) is True:
                    if self.dbEpisodes[media.TheTvDbId][media.Season].has_key(media.Episode) is True:
                        del(self.dbEpisodes[media.TheTvDbId][media.Season][media.Episode])
                        if len(self.dbEpisodes[media.TheTvDbId][media.Season]) == 0:
                            del(self.dbEpisodes[media.TheTvDbId][media.Season])
                        if len(self.dbEpisodes[media.TheTvDbId]) == 0:
                            del(self.dbEpisodes[media.TheTvDbId])
                            if self.dbSeries.has_key(media.TheTvDbId) is True:
                                del(self.dbSeries[media.TheTvDbId])
                
    ##
    # Adds media files to the db
    # @param media: The media file
    # @return: False if file is already in db or movie already in db, else True 
    
    def add(self, media):
        
        if media.isSerie:
            if self.dbSeries.has_key(media.TheTvDbId) is False:
                self.dbSeries[media.TheTvDbId] = media
                return True
            else:
                return False
        
        media.Path = media.Path.replace("\\", "/")
        # Checks if the file is already in db
        if self.checkDuplicate(media.Path, media.Filename, media.Extension):
            return False

        pth = media.Path + "/" + media.Filename + "." + media.Extension
        self.duplicateDetector.append(pth)
        
        if media.isMovie:
            if self.dbMovies.has_key(media.ImdbId) is False:
                self.dbMovies[media.ImdbId] = media
            else: 
                return False
        elif media.isEpisode:
            if self.dbEpisodes.has_key(media.TheTvDbId) is False:
                self.dbEpisodes[media.TheTvDbId] = {}
            
            if self.dbEpisodes[media.TheTvDbId].has_key(media.Season) is False:
                self.dbEpisodes[media.TheTvDbId][media.Season] = {}
            
            if self.dbEpisodes[media.TheTvDbId][media.Season].has_key(media.Episode) is False:
                self.dbEpisodes[media.TheTvDbId][media.Season][media.Episode] = media
            else:
                return False
            
        return True

    def __str__(self):
        epcount = 0
        for key in self.dbSeries:
            if key in self.dbEpisodes:
                for season in self.dbEpisodes[key]:
                    epcount +=  len(self.dbEpisodes[key][season])
        rtv =   unicode(len(self.dbMovies)) + \
                u" " + \
                unicode(len(self.dbSeries)) + \
                u" " + \
                unicode(epcount)
        return Utf8.utf8ToLatin(rtv)

    FAILEDDB = "/hdd/valerie/failed.db"

    MOVIESDB = "/hdd/valerie/movies.db"
    TVSHOWSDB = "/hdd/valerie/tvshows.db"
    EPISODESDB = "/hdd/valerie/episodes.db"

    MOVIESTXD = "/hdd/valerie/movies.txd"
    TVSHOWSTXD = "/hdd/valerie/tvshows.txd"

    MOVIESTXT = "/hdd/valerie/moviedb.txt"
    TVSHOWSTXT = "/hdd/valerie/seriesdb.txt"
    
    DB_TXT = 1
    DB_TXD = 2
    DB_PICKLE = 3
    DB_SQLITE= 4
    USE_DB_VERSION = DB_TXD

    def rmTxt(self):
        try:
            os.remove(self.MOVIESTXT)
        except Exception, ex:
            print ex
        try:
            os.remove(self.TVSHOWSTXT)
        except Exception, ex:
            print ex
            
        ds = DirectoryScanner.DirectoryScanner()
        ds.clear()
        ds.setDirectory("/hdd/valerie/episodes")
        filetypes = []
        filetypes.append("txt")
        ds.listDirectory(filetypes, None, 0)
        for ele in ds.getFileList():
            print "TO BE DELETED:", ele
        #    try:
        #        os.remove(ele[0] + "/" + ele[1] + "." + ele[2])
        #    except Exception, ex:
        #        print ex

    def save(self):
        if self.USE_DB_VERSION == self.DB_TXT:
            self.saveTxt()
        elif self.USE_DB_VERSION == self.DB_TXD:
            self.saveTxd()
            self.rmTxt()
        
        # Always safe pickel as this increses fastsync a lot
        #elif self.USE_DB_VERSION == self.DB_PICKLE:
        self.savePickel()


        
    def saveTxt(self):
        start_time = time.time()    
        f = Utf8.Utf8(u"/hdd/valerie/moviedb.txt", 'w')
        f.write(unicode(date.today()))
        for key in self.dbMovies:
            f.write(self.dbMovies[key].export())
            self.dbMovies[key].setValerieInfoLastAccessTime(self.dbMovies[key].Path)
        #    valeriedbCursor.execute('''insert into movies values (?)''', [(self.dbMovies[key].ImdbId,), (self.dbMovies[key].Title,), (self.dbMovies[key].Year,)] )
        f.close()
        elapsed_time = time.time() - start_time
        print "Took: ", elapsed_time
        
        start_time = time.time()    
        f = Utf8.Utf8(u"/hdd/valerie/seriesdb.txt", 'w')
        f.write(unicode(date.today()))
        for key in self.dbSeries:
            if self.dbEpisodes.has_key(key): # Check if we have episodes for that serie
                f.write(self.dbSeries[key].export())
        f.close()
        elapsed_time = time.time() - start_time
        print "Took (seriesdb.txt): ", elapsed_time

        start_time = time.time()  
        for serie in self.dbEpisodes:
            f = Utf8.Utf8(u"/hdd/valerie/episodes/" + serie + u".txt", 'w')
            f.write(unicode(date.today()))
            for season in self.dbEpisodes[serie]:
                for episode in self.dbEpisodes[serie][season]:
                    f.write(self.dbEpisodes[serie][season][episode].export())
                    self.dbEpisodes[serie][season][episode].setValerieInfoLastAccessTime(self.dbEpisodes[serie][season][episode].Path)
            f.close()
        elapsed_time = time.time() - start_time
        print "Took (episodes/*.txt): ", elapsed_time
        
    def saveTxd(self):
        start_time = time.time()    
        f = Utf8.Utf8(self.MOVIESTXD, 'w')
        f.write(unicode(self.DB_TXD) + u"\n")
        for movie in self.dbMovies.values():
            f.write(movie.exportDefined())
        f.write("EOF\n")
        f.close()
        elapsed_time = time.time() - start_time
        print "Took (episodes/*.txd):", elapsed_time
        
        start_time = time.time()    
        f = Utf8.Utf8(self.TVSHOWSTXD, 'w')
        f.write(unicode(self.DB_TXD) + u"\n")
        for key in self.dbSeries:
            if self.dbEpisodes.has_key(key): # Check if we have episodes for that serie
                f.write(self.dbSeries[key].exportDefined())
        f.write("EOF\n")
        f.close()
        elapsed_time = time.time() - start_time
        print "Took (seriesdb.txd): ", elapsed_time

        start_time = time.time()  
        for serie in self.dbEpisodes:
            f = Utf8.Utf8(u"/hdd/valerie/episodes/" + serie + u".txd", 'w')
            f.write(unicode(self.DB_TXD) + u"\n")
            for season in self.dbEpisodes[serie]:
                for episode in self.dbEpisodes[serie][season].values():
                    f.write(episode.exportDefined())
            f.write("EOF\n")
            f.close()
        elapsed_time = time.time() - start_time
        print "Took (episodes/*.txd): ", elapsed_time
            
    def savePickel(self):
        start_time = time.time()  
        fd = open(self.FAILEDDB, "wb")
        pickle.dump(self.dbFailed, fd, pickle.HIGHEST_PROTOCOL)
        fd.close()
        elapsed_time = time.time() - start_time
        print "Took: ", elapsed_time
        
        start_time = time.time()  
        fd = open(self.MOVIESDB, "wb")
        pickle.dump(self.dbMovies, fd, pickle.HIGHEST_PROTOCOL)
        fd.close()
        elapsed_time = time.time() - start_time
        print "Took: ", elapsed_time
        
        start_time = time.time()  
        fd = open(self.TVSHOWSDB, "wb")
        pickle.dump(self.dbSeries, fd, pickle.HIGHEST_PROTOCOL)
        fd.close()
        elapsed_time = time.time() - start_time
        print "Took (tvshows.db): ", elapsed_time
        
        #start_time = time.time()
        #for serie in self.dbEpisodes:
        #    fd = open(u"/hdd/valerie/episodes/" + serie + u".db", "wb")
        #    pickle.dump(self.dbEpisodes[serie], fd, pickle.HIGHEST_PROTOCOL)
        #    fd.close()
        #elapsed_time = time.time() - start_time
        #print "Took (episodes/*.db): ", elapsed_time
        
        start_time = time.time()
        fd = open(self.EPISODESDB, "wb")
        pickle.dump(self.dbEpisodes, fd, pickle.HIGHEST_PROTOCOL)
        fd.close()
        elapsed_time = time.time() - start_time
        print "Took (episodes.db): ", elapsed_time
        
    def load(self):
        if os.path.isfile(self.FAILEDDB):
            fd = open(self.FAILEDDB, "rb")
            self.dbFailed = pickle.load(fd)
            fd.close()
        
        if os.path.isfile(self.MOVIESDB) and os.path.isfile(self.TVSHOWSDB) and os.path.isfile(self.EPISODESDB):
            self.loadPickle() 
        elif os.path.isfile(self.MOVIESTXD) and os.path.isfile(self.TVSHOWSTXD):
            self.loadTxd() 
        else:
            self.loadTxt() 
    
    def loadTxt(self):
        start_time = time.time()
        try:
            db = Utf8.Utf8(u"/hdd/valerie/moviedb.txt", "r").read()
            if db is not None:
                movies = db.split("\n----END----\n")
                for movie in movies:
                    movie = movie.split("---BEGIN---\n")
                    if len(movie) == 2: 
                        m = MediaInfo("","","")
                        m.importStr(movie[1], True, False, False)
                        path = m.Path + u"/" + m.Filename + u"." + m.Extension
                        #if Config.getBoolean("delete") is False or os.path.isfile(Utf8.utf8ToLatin(path)):
                        #    if m.isValerieInfoAvailable(m.Path):
                        #        if m.getValerieInfoAccessTime(m.Path) == m.getValerieInfoLastAccessTime(m.Path):
                        #            self.add(m)
                        #    else:
                        #        self.add(m)
                        #else:
                        print "Not found: ", Utf8.utf8ToLatin(path)
                        #    print os.path.isfile(Utf8.utf8ToLatin(path))
                        #    print m.getValerieInfoAccessTime(m.Path)
                        #    print m.getValerieInfoLastAccessTime(m.Path)
        except Exception, ex:
            print ex
            print '-'*60
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        
        elapsed_time = time.time() - start_time
        print "Took (moviedb.txt): ", elapsed_time

        start_time = time.time()
        try:
            db = Utf8.Utf8(u"/hdd/valerie/seriesdb.txt", "r").read()
            if db is not None:
                movies = db.split(u"\n----END----\n")
                for movie in movies:
                    movie = movie.split(u"---BEGIN---\n")
                    if len(movie) == 2: 
                        m = MediaInfo("","","")
                        m.importStr(movie[1], False, True, False)
                        self.add(m)
        except Exception, ex:
            print ex
            print '-'*60
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        elapsed_time = time.time() - start_time
        print "Took (seriesdb.txt):", elapsed_time
        
        start_time = time.time()
        try:    
            for key in self.dbSeries:
                db = Utf8.Utf8(u"/hdd/valerie/episodes/" + key + u".txt", "r").read()
                if db is not None:
                    movies = db.split("\n----END----\n")
                    for movie in movies:
                        movie = movie.split("---BEGIN---\n")
                        if len(movie) == 2: 
                            m = MediaInfo("","","")
                            m.importStr(movie[1], False, False, True)
                            path = m.Path + u"/" + m.Filename + u"." + m.Extension
                            if Config.getBoolean("delete") is False or os.path.isfile(Utf8.utf8ToLatin(path)):
                                if m.isValerieInfoAvailable(m.Path):
                                    if m.getValerieInfoAccessTime(m.Path) == m.getValerieInfoLastAccessTime(m.Path):
                                        self.add(m)
                                else:
                                    self.add(m)
                            else:
                                print "Not found: ", Utf8.utf8ToLatin(path)
                                print os.path.isfile(Utf8.utf8ToLatin(path))
                                print m.getValerieInfoAccessTime(m.Path)
                                print m.getValerieInfoLastAccessTime(m.Path)
        except Exception, ex:
            print ex
            print '-'*60
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        elapsed_time = time.time() - start_time
        print "Took (episodes/*.txt): ", elapsed_time
        
        
    def loadTxd(self):
        start_time = time.time()
        try:
            db = Utf8.Utf8(self.MOVIESTXD, "r").read()
            if db is not None:
                lines = db.split("\n")
                version = lines[0]
                linesLen = len(lines)
                for i in range(1, linesLen, 11):
                    if lines[i] == "EOF":
                        break
                    m = MediaInfo()
                    m.importDefined(lines[i:i+11], True, False, False)
                    self.add(m)
        except Exception, ex:
            print ex
            print '-'*60
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        
        elapsed_time = time.time() - start_time
        print "Took (movies.txd): ", elapsed_time

        start_time = time.time()
        try:
            db = Utf8.Utf8(self.TVSHOWSTXD, "r").read()
            if db is not None:
                lines = db.split("\n")
                version = lines[0]
                linesLen = len(lines)
                for i in range(1, linesLen, 9):
                    if lines[i] == "EOF":
                        break
                    m = MediaInfo()
                    m.importDefined(lines[i:i+9], False, True, False)
                    self.add(m)
        except Exception, ex:
            print ex
            print '-'*60
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        
        elapsed_time = time.time() - start_time
        print "Took (tvshows.txd): ", elapsed_time
        
        start_time = time.time()
        try:    
            for key in self.dbSeries:
                db = Utf8.Utf8(u"/hdd/valerie/episodes/" + key + u".txd", "r").read()
                if db is not None:
                    lines = db.split("\n")
                    version = lines[0]
                    linesLen = len(lines)
                    for i in range(1, linesLen, 12):
                        if lines[i] == "EOF":
                            break
                        m = MediaInfo()
                        m.importDefined(lines[i:i+12], False, False, True)
                        self.add(m)
        except Exception, ex:
            print ex
            print '-'*60
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        elapsed_time = time.time() - start_time
        print "Took (episodes/*.txd): ", elapsed_time

    def loadPickle(self):
        start_time = time.time()
        fd = open(self.MOVIESDB, "rb")
        self.dbMovies = pickle.load(fd)
        fd.close()
        elapsed_time = time.time() - start_time
        print "Took (movie.db):", elapsed_time
        
        start_time = time.time()
        fd = open(self.TVSHOWSDB, "rb")
        self.dbSeries = pickle.load(fd)
        fd.close()
        elapsed_time = time.time() - start_time
        print "Took (tvshows.db):", elapsed_time
        
        #start_time = time.time()
        #self.dbEpisodes = {}
        #for key in self.dbSeries:
        #    episode = {}
        #    fd = open(u"/hdd/valerie/episodes/" + key + u".db", "wb")
        #    self.dbEpisodes[key] = pickle.load(fd)
        #    fd.close()
        #elapsed_time = time.time() - start_time
        #print "Took (episodes/*.db): ", elapsed_time
        
        start_time = time.time()
        self.dbEpisodes = {}
        fd = open(self.EPISODESDB, "rb")
        self.dbEpisodes = pickle.load(fd)
        fd.close()
        elapsed_time = time.time() - start_time
        print "Took (episodes.db):", elapsed_time
        