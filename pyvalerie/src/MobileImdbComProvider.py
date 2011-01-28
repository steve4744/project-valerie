'''
Created on 29.11.2010

@author: i7
'''

import re
import WebGrabber
import Utf8

class MobileImdbComProvider():
    '''
    classdocs
    '''
    URL = u"http://m.imdb.com/"
    apiSearch = URL + u"find?q=<search>"
    apiDetails = URL + u"title/<imdbid>/"

    testNoResults = "<div class=\"noResults\">No Results</div>"
        
    class ResultEntry:
        ImdbId = ""
        Title = ""
        IsTVSeries = False
        Year = -1

        def __init__(self):
            self.IsTVSeries = False
            self.Year = -1

        def __str__(self):
            return Utf8.utf8ToLatin(self.Title + u":" + unicode(self.Year) + u":" + self.ImdbId + u":" + unicode(self.IsTVSeries))

    DIV_TITLE_START = u"<div class=\"title\">"
    DIV_TITLE_FLAG = u"<a href="
    DIV_TITLE_END = u"</div>"
    
    def getResults(self, html):
        results = []
        
        htmlSplitted = html.split(self.DIV_TITLE_START)
        for htmlSplitter in htmlSplitted:
            htmlSplitter = htmlSplitter.strip()
            if htmlSplitter.startswith(self.DIV_TITLE_FLAG) is False:
                continue
            
            pos = htmlSplitter.find(self.DIV_TITLE_END)
            if pos < 0:
                continue
            
            entry = self.ResultEntry()
            strEntry = htmlSplitter[0:pos]
            
            if u"TV series" in strEntry: #maybe also miniseries
                entry.IsTVSeries = True;
            
            mImdbId = re.search(r'/title/tt\d*/', strEntry)
            if mImdbId and mImdbId.group():
                sImdbId = mImdbId.group()
                sImdbId = re.sub("/title/", "", sImdbId)
                sImdbId = re.sub("/", "", sImdbId)
                entry.ImdbId = sImdbId;

            mTitle = re.search(r'>.+</a>', strEntry)
            if mTitle and mTitle.group():
                sTitle = mTitle.group();
                sTitle = re.sub("</a>", "", sTitle)
                sTitle = re.sub(">", "", sTitle)
                entry.Title = sTitle;
                
            mYear = re.search(r'\(\d{4}\s?', strEntry)
            if mYear and mYear.group():
                sYear = mYear.group()[1:].strip();
                entry.Year = int(sYear);
                
            if entry.Year > 0: 
                results.append(entry)
        return results
    
    
    DIV_INFO_START = u"<div class=\"mainInfo\">"
    DIV_INFO_END = u"</div>"
    DIV_TAG_START = u"<p>"
    DIV_TAG_END = u"</p>"
    DIV_VOTES_START = u"<div class=\"votes\">"
    DIV_VOTES_END = u"</strong>"
    
    def getInfo(self, html):
        info = html

        pos = info.find(self.DIV_INFO_START)
        if pos < 0:
            return None

        info = info[pos + len(self.DIV_INFO_START):]

        pos = info.find(self.DIV_INFO_END)
        if pos < 0:
            return None

        return info[0:pos].strip()
        
    def getTag(self, info, html):
        print "getTag ->"
        tag = self.getInfo(html)
        if tag is None:
            print "getTag <-", "if tag is None: a"
            return None
        print "tag", tag
        pos = tag.find(self.DIV_TAG_START)
        if pos < 0:
            print "getTag <-", "if pos < 0: b"
            return None
        
        tag = tag[pos + len(self.DIV_TAG_START):]

        pos = tag.find(self.DIV_TAG_END)
        if pos < 0:
            print "getTag <-", "if pos < 0: c"
            return None
        print "getTag", tag
        tag = tag[0:pos]
        tag = tag.strip()
        print "getTag", tag
        info.Tag = tag
        print "getTag <-"
        return info
    
    def getVotes(self, info, html):
        print "getVotes ->"
        votes = html
        
        pos = votes.find(self.DIV_VOTES_START)
        if pos < 0:
            print "getVotes <-", "pos < 0: a"
            return None
        
        votes = votes[pos + len(self.DIV_VOTES_START):]

        pos = votes.find(self.DIV_VOTES_END)
        if pos < 0:
            print "getVotes <-", "pos < 0: b"
            return None

        votes = votes[0:pos]
        
        votes = re.sub("<strong>", "", votes)
        votes = votes.strip()
        
        if len(votes) > 2:
            try:
                votes = votes.split(".")[0]
            except Exception, ex:
                print ex
        
        try:
            info.Popularity = int(votes)
        except Exception, ex:
            print ex
        
        print "getVotes <-"
        return info
    
    ###############################################

    def getMoviesByTitle(self, info):
        
        if info.ImdbId != info.ImdbIdNull:
            info2 = self.getMoviesByImdbID(info)
            if info2 is not None:
                return info2
        
        url = self.apiSearch
        url = re.sub("<search>", info.SearchString, url)
        html = WebGrabber.getHtml(url)

        if html is None:
            print "MobileImdbComProvider::getMoviesByTitle() <- html is None" 
            return None

        if self.testNoResults in html:
            print "MobileImdbComProvider::getMoviesByTitle() <- self.testNoResults in html" 
            return None
        
        print "MIMDB seraches for ", info.isMovie, info.isEpisode, info.isSerie
        
        results = self.getResults(html)
        for result in results:
            if info.isEpisode or info.isSerie:
                if not result.IsTVSeries:
                    continue
            else: # isMovie
                if result.IsTVSeries:
                    continue
            
            info.ImdbId = result.ImdbId
            info.Title = result.Title
            
            
            tmp = self.getMoviesByImdbID(info)
            if tmp is not None:
                info = tmp

            return info
        
        print "Results:\n"
        for result in results:
            print str(result) + "\n"
            
        #exit(0)
        print "MobileImdbComProvider::getMoviesByTitle() <- end reached" 
        return None
        
        
    def getMoviesByImdbID(self, info):
        print "getMoviesByImdbID", info.ImdbId
        url = self.apiDetails
        url = re.sub("<imdbid>", info.ImdbId, url)
        html = WebGrabber.getHtml(url)

        if html is None:
            print "if html is None"
            return None;

        tmp = self.getTag(info, html)
        if tmp is not None:
            info = tmp  

        tmp = self.getVotes(info, html)
        if tmp is not None:
            info = tmp  

        return info;
    
    def getAlternatives(self, info):        
        url = self.apiSearch
        url = re.sub("<search>", info.SearchString, url)
        html = WebGrabber.getHtml(url)

        if html is None:
            print "MobileImdbComProvider::getAlternatives() <- html is None" 
            return None

        if self.testNoResults in html:
            print "MobileImdbComProvider::getAlternatives() <- self.testNoResults in html" 
            return None
        
        results = self.getResults(html)
        return results
    