'''
Created on 23.05.2010

@author: i7
'''

from WebGrabber import WebGrabber
from twisted.web.microdom import parseString

import Config

import re

class TheTvDbProvider(object):
    '''
    classdocs
    '''

    APIKEY = "3A042860EF9F9160";
    apiSearch = "http://www.thetvdb.com/api/GetSeries.php?seriesname=";
    apiSearchEpisode = "http://www.thetvdb.com/api/" + APIKEY + "/series/<seriesid>/default/<season>/<episode>/<lang>.xml";
    apiSearchAllEpisodes = "http://www.thetvdb.com/api/" + APIKEY + "/series/<seriesid>/all/<lang>.xml";
    apiArt = "http://www.thetvdb.com/banners/";
    apiSeriesByID = "http://www.thetvdb.com/data/series/<seriesid>/";
    apiSeriesByImdbID = "http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid="

    def __init__(self):
        '''
        Constructor
        '''

    def getSerieByTitle(self, mediaInfo):
        urlTitle = mediaInfo.Title
        urlTitle = re.sub(" ", "+", urlTitle)
        
        pageHtml = WebGrabber().grab(self.apiSearch + urlTitle)
        
        if not pageHtml:
            return mediaInfo
        
        dom = parseString(pageHtml)
        for p in dom.getElementsByTagName("Series"):
            if p.getElementsByTagName("imdb_id")[0].childNodes[0].data == mediaInfo.ImdbId:
                mediaInfo.TheTvDbId = p.getElementsByTagName("seriesid")[0].childNodes[0].data
                break
        
        return mediaInfo

    def getSerieByImdbID(self, mediaInfo):
        pageHtml = WebGrabber().grab(self.apiSeriesByImdbID + mediaInfo.ImdbId, encoding = "utf-8")
        
        if not pageHtml:
            return mediaInfo
        
        dom = parseString(pageHtml)
        for p in dom.getElementsByTagName("Series"):
            mediaInfo.TheTvDbId = p.getElementsByTagName("seriesid")[0].childNodes[0].data
            o = p.getElementsByTagName("Overview")[0]
            #print p.childNodes
            if len(o.childNodes) > 0:
                print "Overview: ", type(o.childNodes[0].data)
                if type(o.childNodes[0].data) is unicode:
                    print "is unicode"
                    mediaInfo.Plot = o.childNodes[0].data #should be alreay unicode
                else:
                    print "is NOT unicode"
                    mediaInfo.Plot = unicode(o.childNodes[0].nodeValue, "utf-8")
            break
        
        
        
        return mediaInfo

    def getArtByTheTvDbId(self, mediaInfo):
        if mediaInfo.TheTvDbId == "0":
            return mediaInfo
        
        pageHtml = WebGrabber().grab(re.sub("<seriesid>", mediaInfo.TheTvDbId, self.apiSeriesByID))
        
        if not pageHtml:
            return mediaInfo
       
        dom = parseString(pageHtml)
        for p in dom.getElementsByTagName("poster"):
            if len(p.childNodes) > 0:
                mediaInfo.Poster = self.apiArt + p.childNodes[0].data
                break
                
        for p in dom.getElementsByTagName("fanart"):
            if len(p.childNodes) > 0:
                mediaInfo.Backdrop = self.apiArt + p.childNodes[0].data
                break      
        
        return mediaInfo
    
    def getEpisodeByTheTvDbId(self, mediaInfo):
        if mediaInfo.TheTvDbId == "0" or mediaInfo.Season == -1 or mediaInfo.Episode == -1:
            return mediaInfo
        
        url = self.apiSearchEpisode
        
        url = re.sub("<seriesid>", mediaInfo.TheTvDbId, url)
        url = re.sub("<lang>", Config.getKey("local"), url)
        url = re.sub("<season>", unicode(mediaInfo.Season), url)
        url = re.sub("<episode>", unicode(mediaInfo.Episode), url)
        
        
        pageHtml = WebGrabber().grab(url, "utf-8")
        
        if not pageHtml:
            return mediaInfo
       
        dom = parseString(pageHtml)
        for p in dom.getElementsByTagName("EpisodeName"):
            if len(p.childNodes) > 0:
                print "EpisodeName: ", type(p.childNodes[0].data)
                if type(p.childNodes[0].data) is unicode:
                    print "is unicode"
                    mediaInfo.Title = p.childNodes[0].data #should be alreay unicode
                else:
                    print "is NOT unicode"
                    mediaInfo.Title = unicode(p.childNodes[0].nodeValue, "utf-8")
                break
                
        for p in dom.getElementsByTagName("Overview"):
            #print p.childNodes
            if len(p.childNodes) > 0:
                print "Overview: ", type(p.childNodes[0].data)
                if type(p.childNodes[0].data) is unicode:
                    print "is unicode"
                    mediaInfo.Plot = p.childNodes[0].data #should be alreay unicode
                else:
                    print "is NOT unicode"
                    mediaInfo.Plot = unicode(p.childNodes[0].nodeValue, "utf-8")
                break
        #print mediaInfo.Plot
        return mediaInfo
    