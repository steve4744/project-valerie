'''
Created on 15.07.2010

@author: i7
'''
import codecs
from datetime import date
from MediaInfo import MediaInfo

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
        
    def checkDuplicate(self, path, filename, extension):
        pth = path + "/" + filename + "." + extension
        pth = pth.replace("\\", "/")
        #print pth
        return pth in self.duplicateDetector
                
    def add(self, media):
        
        if media.isMovie or media.isEpisode:
            media.Path = media.Path.replace("\\", "/")
            if self.checkDuplicate(media.Path, media.Filename, media.Extension):
                return None
            else:
                pth = media.Path + "/" + media.Filename + "." + media.Extension
                self.duplicateDetector.append(pth)
        
        if media.isMovie:
            self.dbMovies[media.ImdbId] = media
        elif media.isSerie:
            if self.dbSeries.has_key(media.TheTvDbId) is False:
                self.dbSeries[media.TheTvDbId] = media
        elif media.isEpisode:
            if self.dbEpisodes.has_key(media.TheTvDbId) is False:
                self.dbEpisodes[media.TheTvDbId] = {}
            
            if self.dbEpisodes[media.TheTvDbId].has_key(media.Season) is False:
                self.dbEpisodes[media.TheTvDbId][media.Season] = {}
            
            self.dbEpisodes[media.TheTvDbId][media.Season][media.Episode] = media
                
        
        
    def __str__(self):
        return  "dbMovies: " + \
                "\n\t" + str(self.dbMovies) + \
                "\ndbSeries: " + \
                "\n\t" + str(self.dbSeries) + \
                "\ndbEpisodes: " + \
                "\n\t" + str(self.dbEpisodes) + \
                "\n\n" 
                
    def save(self):
        f = open("/hdd/valerie/moviedb.txt", 'wb')
        f.write(str(date.today()))
        for key in self.dbMovies:
            f.write(self.dbMovies[key].export().encode( "utf-8" ))
        f.close()
        
        f = open("/hdd/valerie/seriesdb.txt", 'wb')
        f.write(str(date.today()))
        for key in self.dbSeries:
            f.write(self.dbSeries[key].export().encode( "utf-8" ))
        f.close()
        
        for serie in self.dbEpisodes:
            f = open("/hdd/valerie/episodes/" + serie + ".txt", 'wb')
            f.write(str(date.today()))
            for season in self.dbEpisodes[serie]:
                for episode in self.dbEpisodes[serie][season]:
                    f.write(self.dbEpisodes[serie][season][episode].export().encode( "utf-8" ))
            f.close()
        
    def load(self):
        try:
            db = codecs.open("/hdd/valerie/moviedb.txt", "r", "utf-8").read()[:-1]
            movies = db.split("\n----END----\n")
            for movie in movies:
                movie = movie.split("---BEGIN---\n")
                if len(movie) == 2: 
                    m = MediaInfo("","","")
                    m.importStr(movie[1], True, False, False)
                    self.add(m)
        except Exception, ex:
            print ex
        
        try:
            db = codecs.open("/hdd/valerie/seriesdb.txt", "r", "utf-8").read()[:-1]
            movies = db.split("\n----END----\n")
            for movie in movies:
                movie = movie.split("---BEGIN---\n")
                if len(movie) == 2: 
                    m = MediaInfo("","","")
                    m.importStr(movie[1], False, True, False)
                    self.add(m)
        except Exception, ex:
            print ex
            
        try:    
            for key in self.dbSeries:
                db = codecs.open("/hdd/valerie/episodes/" + key + ".txt", "r", "utf-8").read()[:-1]
                movies = db.split("\n----END----\n")
                for movie in movies:
                    movie = movie.split("---BEGIN---\n")
                    if len(movie) == 2: 
                        m = MediaInfo("","","")
                        m.importStr(movie[1], False, False, True)
                        self.add(m)
        except Exception, ex:
            print ex
            
        print self.duplicateDetector