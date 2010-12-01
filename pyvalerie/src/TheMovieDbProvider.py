'''
Created on 22.05.2010

@author: i7
'''

import WebGrabber
import re

class TheMovieDbProvider(object):
    '''
    classdocs
    '''

    APIKEY = u"7bcd34bb47bc65d20a49b6b446a32866"

    apiImdbLookup = u"http://api.themoviedb.org/2.1/Movie.imdbLookup/<lang>/xml/" + APIKEY + u"/<imdbid>"
    apiGetInfo = u"http://api.themoviedb.org/2.1/Movie.getInfo/<lang>/xml/" + APIKEY + u"/<tmdbid>"

    def getElem(self, elem, name):
        if elem.getElementsByTagName(name) != None:
            if len(elem.getElementsByTagName(name)) > 0:
                if elem.getElementsByTagName(name)[0] != None:
                    if elem.getElementsByTagName(name)[0].childNodes != None:
                        if len(elem.getElementsByTagName(name)[0].childNodes) > 0:
                            return elem.getElementsByTagName(name)[0].childNodes[0]
        return None

    ###
    
    PLOT_MIN_LEN = 10

    def getTmdbId(self, info, elem):
        try:
            eID = self.getElem(elem, "id")
            if eID is not None and eID.data is not None and len(eID.data) > 0:
                info.TmDbId = eID.data
                return info
        except Exception, ex:
            print "TheMovieDbProvider::getTmdbId: ", ex
        return None

    def getName(self, info, elem):
        try:
            eTitle = self.getElem(elem, "name")
            if eTitle is not None and eTitle.data is not None and len(eTitle.data) > 0:
                info.Title = eTitle.data
                return info
        except Exception, ex:
            print "TheMovieDbProvider::getName: ", ex
        return None

    def getOverview(self, info, elem):
        try:
            ePlot = self.getElem(elem, "overview")
            if ePlot is not None and ePlot.data is not None and len(ePlot.data) > self.PLOT_MIN_LEN:
                info.Plot = re.sub(u"\r\n", u" ", ePlot.data)
                info.Plot = re.sub(u"\n", u" ", info.Plot)
                info.Plot += u" [TMDB.ORG]" 
                return info
        except Exception, ex:
            print "TheMovieDbProvider::getOverview: ", ex
        return None

    def getReleased(self, info, elem):
        try:
            eYear = self.getElem(elem, "released")
            if eYear is not None and eYear.data is not None and len(eYear.data) > 0:
                strImdb = eYear.data
                info.Year = int(strImdb[0:strImdb.find(u"-")])
                return info
        except Exception, ex:
            print "TheMovieDbProvider::getReleased: ", ex
        return None

    def getRuntime(self, info, elem):
        try:
            eRuntime = self.getElem(elem, "runtime")
            if eRuntime is not None and eRuntime.data is not None and len(eRuntime.data) > 0:
                info.Runtime = int(eRuntime.data.strip())
                return info
        except Exception, ex:
            print "TheMovieDbProvider::getRuntime: ", ex
        return None
    
    def getRating(self, info, elem):
        try:
            eRating = self.getElem(elem, "rating")
            if eRating is not None and eRating.data is not None and len(eRating.data) > 0:
                strRating = eRating.data
                pos = strRating.find(u".")
                if pos > 0:
                    strRating = strRating[0:pos]
                info.Popularity = int(strRating)
                return info
        except Exception, ex:
            print "TheMovieDbProvider::getRating: ", ex
        return None  
    
    def getTranslated(self, elem):
        try:
            eLang = self.getElem(elem, "translated")
            if eLang is not None and eLang.data is not None and len(eLang.data) > 0:
                if eLang.data == "true":
                    return True
        except Exception, ex:
            print "TheMovieDbProvider::getTranslated: ", ex
        return False
    
    ###############################################
      
      
      
    def getMovieByImdbID(self, info):
        if info.ImdbId == info.ImdbIdNull:
            return None
        
        url = self.apiImdbLookup
        url = re.sub("<imdbid>", info.ImdbId, url)
        url = re.sub("<lang>",   u"en",       url)
        xml = WebGrabber.getXml(url)
        
        if xml is None:
            return None
        
        movieList = xml.getElementsByTagName("movie")
        for eMovie in movieList:
            tmp = self.getTmdbId(info, eMovie)
            if tmp is not None:
                info = tmp
            #tmp = self.getImdbId(info, eMovie)
            #if tmp is not None:
            #    info = tmp
            tmp = self.getName(info, eMovie)
            if tmp is not None:
                info = tmp
            tmp = self.getOverview(info, eMovie)
            if tmp is not None:
                info = tmp
            tmp = self.getReleased(info, eMovie)
            if tmp is not None:
                info = tmp
            tmp = self.getRating(info, eMovie)
            if tmp is not None:
                info = tmp
            tmp = self.getRuntime(info, eMovie)
            if tmp is not None:
                info = tmp
                
            return info
        return None

    def getMovie(self, info, lang):
        if info.TmDbId == info.TmDbIdNull:
            return None
        
        lang = lang.lower()
        
        if lang == u"en":
            return info #en already parsed using getSerieByImdbID()
        
        url = self.apiImdbLookup
        url = re.sub("<imdbid>", info.ImdbId, url)
        url = re.sub("<lang>",   lang,        url)
        xml = WebGrabber.getXml(url)
        
        if xml is None:
            return None
        
        movieList = xml.getElementsByTagName("movie")
        for eMovie in movieList:
            
            if self.getTranslated(eMovie) is False:
                continue
            
            #tmp = self.getTmdbId(info, eMovie)
            #if tmp is not None:
            #    info = tmp
            #tmp = self.getImdbId(info, eMovie)
            #if tmp is not None:
            #    info = tmp
            tmp = self.getName(info, eMovie)
            if tmp is not None:
                info = tmp
            tmp = self.getOverview(info, eMovie)
            if tmp is not None:
                info = tmp
            tmp = self.getReleased(info, eMovie)
            if tmp is not None:
                info = tmp
            tmp = self.getRating(info, eMovie)
            if tmp is not None:
                info = tmp
            tmp = self.getRuntime(info, eMovie)
            if tmp is not None:
                info = tmp
                
            return info
        return None
    
    
      
    def getArtByImdbId(self, info):
        if info.ImdbId == info.ImdbIdNull:
            return None
        
        url = self.apiImdbLookup
        url = re.sub("<imdbid>", info.ImdbId, url)
        url = re.sub("<lang>",   u"en",       url)
        xml = WebGrabber.getXml(url)
        
        if xml is None:
            return None
        
        movieList = xml.getElementsByTagName("movie")
        for eMovie in movieList:
            for p in eMovie.getElementsByTagName("image"):
                if p.getAttribute("type") == "poster":
                    if p.getAttribute("size") == "cover":
                        info.Poster = p.getAttribute("url")
                elif p.getAttribute("type") == "backdrop":
                    if p.getAttribute("size") == "original":
                        info.Backdrop = p.getAttribute("url")
                        
                if len(info.Poster) > 0 and len(info.Backdrop) > 0:
                    return info
            return info
        return None
        
        
