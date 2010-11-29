'''
Created on 15.07.2010

@author: i7
'''

import os
from datetime import date
from MediaInfo import MediaInfo
import Utf8

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
        
        self.duplicateDetector = []
        
    def reload(self):
        self.dbMovies = {}
        self.dbSeries = {}
        self.dbEpisodes = {}
        
        self.duplicateDetector = []
        
        self.load()
        
    ##
    # Checks if file is already in the db
    # @param path: utf-8 
    # @param filename: utf-8 
    # @param extension: utf-8 
    # @return: True if already in db, False if not
        
    def checkDuplicate(self, path, filename, extension):
        pth = path + "/" + filename + "." + extension
        if pth in self.duplicateDetector:
            return True
        else:
            return False
                
    ##
    # Adds media files to the db
    # @param media: The media file
    # @return: False if file is already in db else True 
    
    def add(self, media):
        
        if media.isSerie:
            if self.dbSeries.has_key(media.TheTvDbId) is False:
                self.dbSeries[media.TheTvDbId] = media
                return True
            else:
                return False
        
        media.Path = media.Path.replace("\\", "/")
        if self.checkDuplicate(media.Path, media.Filename, media.Extension):
            return False

        pth = media.Path + "/" + media.Filename + "." + media.Extension
        self.duplicateDetector.append(pth)
        
        if media.isMovie:
            self.dbMovies[media.ImdbId] = media
        elif media.isEpisode:
            if self.dbEpisodes.has_key(media.TheTvDbId) is False:
                self.dbEpisodes[media.TheTvDbId] = {}
            
            if self.dbEpisodes[media.TheTvDbId].has_key(media.Season) is False:
                self.dbEpisodes[media.TheTvDbId][media.Season] = {}
            
            self.dbEpisodes[media.TheTvDbId][media.Season][media.Episode] = media
            
        return True

    def __str__(self):
        rtv =   unicode(len(self.dbMovies)) + \
                u" " + \
                unicode(len(self.dbSeries)) + \
                u" " + \
                unicode(len(self.dbEpisodes))
        return Utf8.utf8ToLatin(rtv)

    def save(self):
        f = Utf8.Utf8(u"/hdd/valerie/moviedb.txt", 'w')
        f.write(unicode(date.today()))
        for key in self.dbMovies:
            f.write(self.dbMovies[key].export())
            self.dbMovies[key].setValerieInfoLastAccessTime(self.dbMovies[key].Path)
        f.close()
        
        f = Utf8.Utf8(u"/hdd/valerie/seriesdb.txt", 'w')
        f.write(unicode(date.today()))
        for key in self.dbSeries:
            if self.dbEpisodes.has_key(key): # Check if we have episodes for that serie
                f.write(self.dbSeries[key].export())
        f.close()
        
        for serie in self.dbEpisodes:
            f = Utf8.Utf8(u"/hdd/valerie/episodes/" + serie + u".txt", 'w')
            f.write(unicode(date.today()))
            for season in self.dbEpisodes[serie]:
                for episode in self.dbEpisodes[serie][season]:
                    f.write(self.dbEpisodes[serie][season][episode].export())
                    self.dbEpisodes[serie][season][episode].setValerieInfoLastAccessTime(self.dbEpisodes[serie][season][episode].Path)
            f.close()

    def load(self):
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
                        if os.path.isfile(Utf8.utf8ToLatin(path)):
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
                            if os.path.isfile(Utf8.utf8ToLatin(path)):
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
            
        #print self.duplicateDetector
