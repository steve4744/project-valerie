'''
Created on 22.05.2010

@author: i7
'''

from WebGrabber import WebGrabber
from twisted.web.microdom import parseString
from HtmlEncoding import decode_htmlentities

import Config

class TheMovieDbProvider(object):
    '''
    classdocs
    '''

    APIKEY = "7bcd34bb47bc65d20a49b6b446a32866";
    #apiImdbLookup = "http://api.themoviedb.org/2.0/Movie.imdbLookup?api_key=" + APIKEY + "&imdb_id=";
    apiImdbLookup = "http://api.themoviedb.org/2.1/Movie.imdbLookup/"
    apiImdbLookup2 = "/xml/" + APIKEY + "/"
    apiSearch = "http://api.themoviedb.org/2.0/Movie.search?api_key=" + APIKEY + "&title=";
    apiGetInfo = "http://api.themoviedb.org/2.0/Movie.getInfo?api_key=" + APIKEY + "=";

    def __init__(self):
        '''
        Constructor
        '''
      
    def getMovieByImdbID(self, mediaInfo):
        if mediaInfo.ImdbId == "tt0000000":
            return mediaInfo
        
        pageHtml = WebGrabber().grab(self.apiImdbLookup + Config.getKey("local") + self.apiImdbLookup2 + mediaInfo.ImdbId)
        
        if not pageHtml:
            return mediaInfo
       
        pageHtml = decode_htmlentities(pageHtml)
        try:
            dom = parseString(pageHtml)
        except Exception, ex:
            print ex
            return mediaInfo
        
        for p in dom.getElementsByTagName("name"):
            if len(p.childNodes) > 0:
                mediaInfo.Title = p.childNodes[0].data.strip()
            
        for p in dom.getElementsByTagName("overview"):
            if len(p.childNodes) > 0:
                mediaInfo.Plot = p.childNodes[0].data.strip()
      
        return mediaInfo
      
    def getArtByImdbId(self, mediaInfo):
        if mediaInfo.ImdbId == "tt0000000":
            return mediaInfo
        
        pageHtml = WebGrabber().grab(self.apiImdbLookup + Config.getKey("local") + self.apiImdbLookup2 + mediaInfo.ImdbId)
        
        if not pageHtml:
            return mediaInfo
       
        dom = parseString(pageHtml)
        for p in dom.getElementsByTagName("image"):
            if p.getAttribute("type") == "poster":
                if p.getAttribute("size") == "cover":
                    mediaInfo.Poster = p.getAttribute("url")
            elif p.getAttribute("type") == "backdrop":
                if p.getAttribute("size") == "original":
                    mediaInfo.Backdrop = p.getAttribute("url")
        
        return mediaInfo
