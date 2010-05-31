'''
Created on 22.05.2010

@author: i7
'''

from WebGrabber import WebGrabber
from twisted.web.microdom import parseString

class TheMovieDbProvider(object):
    '''
    classdocs
    '''

    APIKEY = "7bcd34bb47bc65d20a49b6b446a32866";
    apiImdbLookup = "http://api.themoviedb.org/2.0/Movie.imdbLookup?api_key=" + APIKEY + "&imdb_id=";
    apiSearch = "http://api.themoviedb.org/2.0/Movie.search?api_key=" + APIKEY + "&title=";
    apiGetInfo = "http://api.themoviedb.org/2.0/Movie.getInfo?api_key=" + APIKEY + "=";

    def __init__(self):
        '''
        Constructor
        '''
      
    def getArtByImdbId(self, mediaInfo):
        if mediaInfo.ImdbId == "tt0000000":
            return mediaInfo
        
        pageHtml = WebGrabber().grab(self.apiImdbLookup + mediaInfo.ImdbId)
        
        if not pageHtml:
            return mediaInfo
       
        dom = parseString(pageHtml)
        for p in dom.getElementsByTagName("poster"):
            if p.getAttribute("size") == "mid":
                mediaInfo.Poster = p.childNodes[0].data
                
        for p in dom.getElementsByTagName("backdrop"):
            if p.getAttribute("size") == "original":
                mediaInfo.Backdrop = p.childNodes[0].data
        
        return mediaInfo
