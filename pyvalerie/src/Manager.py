'''
Created on 18.12.2010

@author: i7
'''
from Database import Database
from MediaInfo import MediaInfo
from MobileImdbComProvider import MobileImdbComProvider
import replace
import Config

class Manager(object):
    '''
    classdocs
    '''

    MOVIES = 0
    TVSHOWS = 1
    TVSHOWSEPISODES = 2
    FAILED = 3


    def __init__(self):
        '''
        Constructor
        '''
        
    def start(self):
        Config.load()
        self.db = Database()
        self.db.reload()
        
        replace.load()
    
    def finish(self):
        self.db.save()
    
    def getAll(self, type, param=None):
        if type == self.MOVIES:
            return self.db.dbMovies.values()
        elif type == self.TVSHOWS:
            list = []
            for serie in self.db.dbEpisodes:
                for season in self.db.dbEpisodes[serie]:
                    list += self.db.dbEpisodes[serie][season].values()
            return list
        elif type == self.FAILED:
            return self.db.dbFailed
        else:
            return None
        
    def searchAlternatives(self, oldElement):
        element = MediaInfo(oldElement.Path, oldElement.Filename, oldElement.Extension)
        if type(oldElement) is MediaInfo:    
            element.isMovie = oldElement.isMovie
            element.isSerie = oldElement.isSerie
        element.parse()
        print "SEARCH", element.SearchString
        return MobileImdbComProvider().getAlternatives(element)
        
    def syncElement(self, path, filename, extension, imdbid, istvshow):
        print "Manager::syncElement", path, filename, extension, imdbid, istvshow
        from sync import Sync
        element = MediaInfo(path, filename, extension)
        element.parse()
        element.ImdbId = imdbid
        if istvshow:
            element.isSerie = True
            element.isMovie = False
        else:
            element.isSerie = False
            element.isMovie = True
        
        results = Sync().syncWithId(element)
        if results is not None:
            return results
        else:
            if istvshow is False:
                element.isSerie = True
                element.isMovie = False
            else:
                element.isSerie = False
                element.isMovie = True
            
            results = Sync().syncWithId(element)
            if results is not None:
                return results
        return None
    
    def replace(self, oldElement, newElement):
        print "Manager::replace", oldElement, newElement
        if oldElement is not None:
            if type(oldElement) is MediaInfo:
                self.db.remove(oldElement)
            else:
                self.db.removeFailed(oldElement)
        
        if newElement is not None:               
            if len(newElement) == 2:
                self.db.add(newElement[0])
                self.db.add(newElement[1])
            else:
                self.db.add(newElement[0])
                