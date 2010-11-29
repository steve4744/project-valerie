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
            
            if u"TV series" in strEntry:
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
            results.append(entry)
        return results
    
    ###############################################

    def getMoviesByTitle(self, info):
        
        url = self.apiSearch
        url = re.sub("<search>", info.SearchString, url)
        html = WebGrabber.getHtml(url)

        if html is None:
            print "MobileImdbComProvider::getMoviesByTitle() <- html is None" 
            return None

        if self.testNoResults in html:
            print "MobileImdbComProvider::getMoviesByTitle() <- self.testNoResults in html" 
            return None
        
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
            return info
        
        print "Results:\n"
        for result in results:
            print str(result) + "\n"
            
        #exit(0)
        print "MobileImdbComProvider::getMoviesByTitle() <- end reached" 
        return None
        
        
        
    